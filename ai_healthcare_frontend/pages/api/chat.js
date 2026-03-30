// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Only POST allowed' });
  }

  const { symptoms, history } = req.body;

  if (!symptoms) {
    return res.status(400).json({ error: 'Symptoms are required' });
  }

  // Determine if OPENAI API key is available
  const apiKey = process.env.OPENAI_API_KEY;

  if (apiKey) {
    try {
      // Basic implementation of OpenAI call
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [
            {
              role: "system",
              content: "You are an AI healthcare assistant. Analyze the symptoms provided. Output MUST BE a generic JSON object with keys: diagnosis (string), recommended_doctor (string: General Physician / Cardiologist / Dermatologist / etc), urgency (string: Normal / Follow-up / Immediate), confidence (string percentage)."
            },
            {
              role: "user",
              content: `Symptoms: ${symptoms}\nHistory: ${history || 'None'}`
            }
          ]
        })
      });

      const data = await response.json();
      if (data.choices && data.choices[0]) {
        try {
          const aiContent = JSON.parse(data.choices[0].message.content);
          return res.status(200).json(aiContent);
        } catch (e) {
          // Fallback if not strictly JSON
          return res.status(200).json({
            diagnosis: data.choices[0].message.content,
            recommended_doctor: "General Physician",
            urgency: "Follow-up",
            confidence: "80%"
          });
        }
      }
    } catch (err) {
      console.error("OpenAI error", err);
    }
  }

  // Fallback Mock output if no API key or error
  // Simple keyword matching for the mock
  const s = symptoms.toLowerCase();
  let diagnosis = "Mild Viral Infection";
  let urgency = "Normal";
  let recommended_doctor = "General Physician";
  let confidence = "85%";

  if (s.includes('chest pain') || s.includes('heart')) {
    diagnosis = "Potential Cardiac Issue";
    urgency = "Immediate";
    recommended_doctor = "Cardiologist";
    confidence = "92%";
  } else if (s.includes('skin') || s.includes('rash')) {
    diagnosis = "Dermatitis / Allergic Reaction";
    urgency = "Follow-up";
    recommended_doctor = "Dermatologist";
    confidence = "88%";
  } else if (s.includes('headache') || s.includes('migraine')) {
    diagnosis = "Migraine / Tension Headache";
    urgency = "Normal";
    recommended_doctor = "Neurologist";
    confidence = "90%";
  } else if (s.includes('breathing') || s.includes('cough')) {
    diagnosis = "Respiratory Infection / Asthma";
    urgency = "Follow-up";
    recommended_doctor = "Pulmonologist";
    confidence = "85%";
  }

  // Simulating network delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  res.status(200).json({
    diagnosis,
    recommended_doctor,
    urgency,
    confidence,
    notice: apiKey ? undefined : "Simulated response (No OpenAI API Key provided)"
  });
}
