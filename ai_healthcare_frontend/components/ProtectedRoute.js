import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { jwtDecode } from 'jwt-decode';

export default function ProtectedRoute({ children, allowedRoles = [] }) {
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

        if (allowedRoles.length > 0) {
          const role = (decoded.role || 'patient').toLowerCase();
          if (!allowedRoles.includes(role)) {
            router.replace('/auth/login'); // Or a 403 unauthorized page
            return;
          }
        }

        setIsAuthorized(true);
      } catch (err) {
        localStorage.removeItem('token');
        router.replace('/auth/login');
      }
    };

    checkAuth();
  }, [router, allowedRoles]);

  if (!isAuthorized) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50">Loading...</div>;
  }

  return <>{children}</>;
}
