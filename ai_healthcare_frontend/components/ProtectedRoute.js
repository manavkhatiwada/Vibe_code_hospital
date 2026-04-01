import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { jwtDecode } from 'jwt-decode';

export default function ProtectedRoute({
  children,
  allowedRoles = [],
  requireSuperAdmin = false,
  forbidSuperAdmin = false,
}) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.replace('/auth/login');
        return;
      }

      try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decoded.exp < currentTime) {
          localStorage.removeItem('token');
          router.replace('/auth/login');
          return;
        }

        // Check role if specified
        if (allowedRoles.length > 0) {
          const role = (decoded.role || 'patient').toLowerCase();
          if (!allowedRoles.includes(role)) {
            router.replace('/auth/login'); // Or a 403 unauthorized page
            return;
          }
        }

        // Check super-admin if required
        if (requireSuperAdmin && !decoded.is_superuser) {
          router.replace('/auth/login'); // Redirect non-superadmins
          return;
        }

        // Hospital-admin pages can explicitly block platform super-admins.
        if (forbidSuperAdmin && decoded.is_superuser) {
          router.replace('/admin/dashboard');
          return;
        }

        setIsAuthorized(true);
      } catch (err) {
        localStorage.removeItem('token');
        router.replace('/auth/login');
      }
    };

    checkAuth();
  }, [router, allowedRoles, requireSuperAdmin, forbidSuperAdmin]);

  if (!isAuthorized) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50">Loading...</div>;
  }

  return <>{children}</>;
}

// Helper function for getInitialProps
export function getServerSideProtectedProps(ctx, allowedRoles = [], requireSuperAdmin = false) {
  const token = ctx.req?.headers?.cookie?.split('; ')?.find(c => c.startsWith('token='))?.substring(6);

  if (!token && typeof window === 'undefined') {
    return {
      redirect: {
        destination: '/auth/login',
        permanent: false,
      },
    };
  }

  return { props: {} };
}
