export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Only POST allowed' });
  }

  const { symptoms, history } = req.body;
  if (!symptoms) {
    return res.status(400).json({ error: 'Symptoms are required' });
  }

  const specialtyFallbacks = {
    'general physician': 'General Medicine',
    cardiologist: 'Cardiology',
    dermatologist: 'Dermatology',
    neurologist: 'Neurology',
    pulmonologist: 'Pulmonology',
    gastroenterologist: 'Gastroenterology',
    orthopedist: 'Orthopedics',
    endocrinologist: 'Endocrinology',
    ent: 'ENT',
  };

  const toStructuredResponse = (payload, notice) => {
    const recommendedDoctor = payload.recommended_doctor || 'General Physician';
    const recommendedSpecialty =
      specialtyFallbacks[recommendedDoctor.toLowerCase()] || recommendedDoctor;
    return {
      diagnosis: payload.diagnosis || 'General assessment not available',
      recommended_doctor: recommendedDoctor,
      recommended_specialty: recommendedSpecialty,
      urgency: payload.urgency || 'Follow-up',
      confidence: payload.confidence || '75%',
      care_path:
        payload.care_path ||
        'Please consult a licensed clinician for final diagnosis and treatment plan.',
      notice,
    };
  };

  const apiKey = process.env.GEMINI_API_KEY;

  if (apiKey) {
    const prompt = `You are a medical AI assistant. A patient describes their symptoms. Respond ONLY with a valid JSON object — no markdown, no explanation, just raw JSON.

Required JSON keys:
- diagnosis (string): most likely condition
- recommended_doctor (string): one of — General Physician, Cardiologist, Dermatologist, Neurologist, Pulmonologist, Gastroenterologist, Orthopedist, Endocrinologist, ENT
- urgency (string): one of — Normal, Follow-up, Immediate
- confidence (string): percentage like "85%"
- care_path (string): one sentence of actionable advice

Patient symptoms: ${symptoms}
${history ? `Previous conversation context: ${history}` : ''}`;

    try {
      const geminiRes = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.3, maxOutputTokens: 512 },
          }),
        }
      );

      const geminiData = await geminiRes.json();
      const rawText = geminiData?.candidates?.[0]?.content?.parts?.[0]?.text || '';

      // Strip markdown code fences if Gemini wraps the JSON
      const cleaned = rawText.replace(/```json\s*/gi, '').replace(/```\s*/g, '').trim();

      try {
        const parsed = JSON.parse(cleaned);
        return res.status(200).json(toStructuredResponse(parsed));
      } catch {
        // Gemini responded but not valid JSON — wrap the text
        return res.status(200).json(
          toStructuredResponse({
            diagnosis: cleaned || 'Unable to parse AI response',
            recommended_doctor: 'General Physician',
            urgency: 'Follow-up',
            confidence: '70%',
            care_path: 'Please consult a licensed clinician for a proper evaluation.',
          })
        );
      }
    } catch (err) {
      console.error('Gemini API error:', err);
    }
  }

  // Keyword-based fallback when no key or API call fails
  const s = symptoms.toLowerCase();
  let diagnosis = 'Mild Viral Infection';
  let urgency = 'Normal';
  let recommended_doctor = 'General Physician';
  let confidence = '85%';

  if (s.includes('chest pain') || s.includes('heart')) {
    diagnosis = 'Potential Cardiac Issue';
    urgency = 'Immediate';
    recommended_doctor = 'Cardiologist';
    confidence = '92%';
  } else if (s.includes('skin') || s.includes('rash')) {
    diagnosis = 'Dermatitis / Allergic Reaction';
    urgency = 'Follow-up';
    recommended_doctor = 'Dermatologist';
    confidence = '88%';
  } else if (s.includes('headache') || s.includes('migraine')) {
    diagnosis = 'Migraine / Tension Headache';
    urgency = 'Normal';
    recommended_doctor = 'Neurologist';
    confidence = '90%';
  } else if (s.includes('breathing') || s.includes('cough')) {
    diagnosis = 'Respiratory Infection / Asthma';
    urgency = 'Follow-up';
    recommended_doctor = 'Pulmonologist';
    confidence = '85%';
  }

  await new Promise((resolve) => setTimeout(resolve, 800));

  return res.status(200).json(
    toStructuredResponse(
      { diagnosis, recommended_doctor, urgency, confidence, care_path: 'Choose a suitable hospital and book with the suggested specialist.' },
      'Simulated response (No Gemini API Key active)'
    )
  );
}
