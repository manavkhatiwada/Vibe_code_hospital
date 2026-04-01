import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import api from '../utils/api';

const SPECIALTY_ALIASES = {
  'general physician': ['general medicine', 'family medicine', 'internal medicine', 'general'],
  cardiologist: ['cardiology', 'cardio'],
  dermatologist: ['dermatology', 'skin'],
  neurologist: ['neurology', 'neuro'],
  pulmonologist: ['pulmonology', 'respiratory'],
  gastroenterologist: ['gastroenterology', 'gastro'],
  orthopedist: ['orthopedics', 'orthopedic'],
  endocrinologist: ['endocrinology', 'hormone'],
  ent: ['ent', 'ear nose throat'],
};

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const buildHospitalRecommendations = async (recommendedDoctor) => {
    try {
      const { data: doctors } = await api.get('/doctors/');
      const label = (recommendedDoctor || 'General Physician').toLowerCase();
      const aliases = SPECIALTY_ALIASES[label] || [label];

      const matchedDoctors = (doctors || []).filter((doctor) => {
        const specialization = (doctor.specialization || '').toLowerCase();
        return aliases.some((alias) => specialization.includes(alias));
      });

      const scopedDoctors = matchedDoctors.length ? matchedDoctors : (doctors || []).slice(0, 8);
      const byHospital = new Map();

      scopedDoctors.forEach((doctor) => {
        const doctorHospitals = Array.isArray(doctor.hospitals) && doctor.hospitals.length
          ? doctor.hospitals
          : (doctor.hospital ? [doctor.hospital] : []);

        doctorHospitals.forEach((hospital) => {
          const key = hospital.id;
          if (!byHospital.has(key)) {
            byHospital.set(key, {
              id: hospital.id,
              name: hospital.name,
              city: hospital.city,
              state: hospital.state,
              specialists: [],
            });
          }
          const card = byHospital.get(key);
          if (!card.specialists.includes(doctor.user_username)) {
            card.specialists.push(doctor.user_username);
          }
        });
      });

      return Array.from(byHospital.values())
        .sort((a, b) => b.specialists.length - a.specialists.length)
        .slice(0, 3);
    } catch (err) {
      return [];
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    let mounted = true;

    const bootstrapConversation = async () => {
      try {
        const { data: conversations } = await api.get('/chatbot/conversations/');

        let activeConversation = conversations?.[0];
        if (!activeConversation) {
          const created = await api.post('/chatbot/conversations/', {});
          activeConversation = created.data;
        }

        if (!mounted) return;
        setConversationId(activeConversation.id);

        const { data: history } = await api.get(`/chatbot/conversations/${activeConversation.id}/messages/`);
        if (!mounted) return;

        if (history?.length) {
          setMessages(
            history
              .filter((msg) => msg.sender_type === 'USER' || msg.sender_type === 'ASSISTANT')
              .map((msg) => ({
                role: msg.sender_type === 'USER' ? 'user' : 'assistant',
                content: msg.message_text,
                recommendations: null,
              }))
          );
        } else {
          setMessages([
            {
              role: 'assistant',
              content:
                'Hello! I am your AI Healthcare Assistant. Please describe your symptoms and I will provide an initial assessment.',
              recommendations: null,
            },
          ]);
        }
      } catch (err) {
        if (!mounted) return;
        setMessages([
          {
            role: 'assistant',
            content:
              'Hello! I am your AI Healthcare Assistant. Please describe your symptoms and I will provide an initial assessment.',
            recommendations: null,
          },
        ]);
      } finally {
        if (mounted) {
          setBootstrapping(false);
        }
      }
    };

    bootstrapConversation();

    return () => {
      mounted = false;
    };
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setInput('');
    setLoading(true);

    try {
      // POST to our Next.js API route
      const res = await axios.post('/api/chat', { symptoms: userMsg });
      const data = res.data;
      const hospitals = await buildHospitalRecommendations(data.recommended_doctor);

      const aiResponse = `
**Possible Diagnosis**: ${data.diagnosis}
**Recommended Doctor**: ${data.recommended_doctor}
    **Recommended Specialty**: ${data.recommended_specialty || data.recommended_doctor}
**Urgency**: ${data.urgency}
**Confidence**: ${data.confidence}
    **Care Path**: ${data.care_path || 'Consult a licensed clinician for final diagnosis.'}
${data.notice ? `\n*(Note: ${data.notice})*` : ''}
      `;

      if (conversationId) {
        const persisted = await api.post(
          `/chatbot/conversations/${conversationId}/messages/`,
          {
            message_text: userMsg,
            assistant_message_text: aiResponse.trim(),
          }
        );

        setMessages((prev) => [
          ...prev,
          {
            role: 'user',
            content: persisted.data.user_message.message_text,
          },
          {
            role: 'assistant',
            content: persisted.data.assistant_message.message_text,
            recommendations: {
              specialty: data.recommended_specialty || data.recommended_doctor,
              hospitals,
            },
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'user', content: userMsg },
          {
            role: 'assistant',
            content: aiResponse.trim(),
            recommendations: {
              specialty: data.recommended_specialty || data.recommended_doctor,
              hospitals,
            },
          },
        ]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'user', content: userMsg },
        {
          role: 'assistant',
          content: "I'm sorry, I am currently unable to process your symptoms due to a system error.",
          recommendations: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (bootstrapping) {
    return (
      <div className="flex items-center justify-center h-150 w-full max-w-2xl bg-white border border-gray-200 rounded-2xl shadow-xl">
        <p className="text-gray-500">Loading conversation...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-150 w-full max-w-2xl bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-blue-600 p-4 text-white flex justify-between items-center">
        <div>
          <h3 className="font-bold text-lg flex items-center gap-2">🤖 AI Symptom Checker</h3>
          <p className="text-blue-100 text-xs mt-1">Instant preliminary analysis</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl whitespace-pre-wrap ${msg.role === 'user'
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-white border border-gray-100 shadow-sm text-gray-800 rounded-bl-none'
              }`}>
              {msg.content}
              {msg.role === 'assistant' && msg.recommendations?.hospitals?.length > 0 && (
                <div className="mt-4 border-t pt-3">
                  <p className="text-xs font-semibold text-gray-700 mb-2">
                    Suggested hospitals for {msg.recommendations.specialty}
                  </p>
                  <div className="space-y-2">
                    {msg.recommendations.hospitals.map((hospital) => (
                      <div key={hospital.id} className="rounded-lg border border-blue-100 bg-blue-50 p-2">
                        <p className="text-sm font-semibold text-blue-800">{hospital.name}</p>
                        <p className="text-xs text-blue-700">{hospital.city}, {hospital.state}</p>
                        <p className="text-xs text-blue-700">
                          Available doctors: {hospital.specialists.slice(0, 3).join(', ')}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm p-4 rounded-2xl rounded-bl-none text-gray-500 animate-pulse flex space-x-2">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100 flex gap-2 w-full">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Describe your symptoms (e.g. I have a severe headache...)"
          className="flex-1 px-4 py-3 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 transition shadow-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white w-12 h-12 flex items-center justify-center rounded-full hover:bg-blue-700 disabled:bg-blue-300 transition shadow-md"
        >
          ➤
        </button>
      </form>
    </div>
  );
}
