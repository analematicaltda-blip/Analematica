import { GoogleGenAI, Chat, GenerateContentResponse, Modality, LiveServerMessage, Type, FunctionDeclaration } from "@google/genai";
import type { GroundingChunk, LLMProvider } from '../types';

// Ensure API_KEY is available.
if (!process.env.API_KEY) {
  console.warn("API_KEY environment variable not set. Using a placeholder.");
  process.env.API_KEY = "YOUR_API_KEY";
}

let ai: GoogleGenAI;
const getAiClient = () => {
    if (!ai) {
        ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });
    }
    return ai;
}

// --- OLLAMA IMPLEMENTATIONS ---
const ollamaGenerate = async (endpoint: string, model: string, prompt: string, format?: 'json'): Promise<any> => {
    const response = await fetch(`${endpoint}/api/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: model,
            prompt: prompt,
            stream: false,
            format: format
        }),
    });
    if (!response.ok) {
        throw new Error(`Ollama request failed with status ${response.status}`);
    }
    const data = await response.json();
    return data.response;
}

// --- HYBRID SERVICE FUNCTIONS ---

interface ProviderConfig {
  ollamaEndpoint: string;
  model: string;
}

export const generateText = async (provider: LLMProvider, config: ProviderConfig, prompt: string): Promise<string> => {
  try {
    if (provider === 'ollama') {
        return await ollamaGenerate(config.ollamaEndpoint, config.model, prompt);
    }
    // Default to gemini
    const ai = getAiClient();
    const response = await ai.models.generateContent({ model: config.model, contents: prompt });
    return response.text;
  } catch (error) {
    console.error(`Error generating text with ${provider}:`, error);
    return "Lo siento, no pude generar una respuesta.";
  }
};

// --- NUEVA FUNCIÓN PARA LA FASE 3 ---
export const generateTextFromBackend = async (prompt: string, authToken: string): Promise<string> => {
  try {
    const response = await fetch('/api/ai/text', { // Asumiendo que el proxy de Vite está configurado
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ prompt: prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Error ${response.status}`);
    }

    const data = await response.json();
    return data.result;
  } catch (error) {
    console.error('Error generating text from backend:', error);
    return "Lo siento, hubo un error al generar el texto desde el backend.";
  }
};

export const analyzeMessage = async (provider: LLMProvider, config: ProviderConfig, message: string): Promise<{ sentiment: 'positive' | 'neutral' | 'negative', tags: string[] }> => {
    try {
        if (provider === 'ollama') {
            const prompt = `Analyze the following message. Respond ONLY with a valid JSON object with two keys: "sentiment" (which can be "positive", "neutral", or "negative") and "tags" (an array of up to 3 relevant string tags). Message: "${message}"`;
            const responseJsonString = await ollamaGenerate(config.ollamaEndpoint, config.model, prompt, 'json');
            return JSON.parse(responseJsonString);
        }

        // Gemini implementation
        const ai = getAiClient();
        const response = await ai.models.generateContent({
            model: config.model,
            contents: `Analiza el siguiente mensaje de cliente. Determina el sentimiento (positive, neutral, o negative) y extrae hasta 3 etiquetas relevantes (ej: 'pregunta', 'queja', 'stock', 'precio'). Mensaje: "${message}"`,
            config: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: Type.OBJECT,
                    properties: {
                        sentiment: { type: Type.STRING, enum: ['positive', 'neutral', 'negative'] },
                        tags: {
                            type: Type.ARRAY,
                            items: { type: Type.STRING }
                        }
                    },
                    required: ['sentiment', 'tags']
                }
            }
        });
        return JSON.parse(response.text);
    } catch (error) {
        console.error(`Error analyzing message with ${provider}:`, error);
        return { sentiment: 'neutral', tags: ['error_analisis'] };
    }
}


// --- GEMINI-ONLY FUNCTIONS ---

export const getSalesForecast = async (historicalData: {month: string, sales: number}[]): Promise<{month: string, forecast: number}[]> => {
    // In a real scenario, you'd make a call to Gemini with the data.
    // Here, we simulate the AI's response for a quick and stable UI demo.
    console.log("Simulating AI sales forecast with data:", historicalData);
    
    // Simple simulation logic
    const lastMonth = historicalData[historicalData.length - 1];
    const secondLastMonth = historicalData[historicalData.length - 2];
    const trend = (lastMonth.sales - secondLastMonth.sales) / 2;
    
    const forecast = [];
    let lastValue = lastMonth.sales;
    const months = ["Jun", "Jul", "Ago"];

    for(const month of months) {
        lastValue += trend * (1 + (Math.random() - 0.5) * 0.2); // Add some noise
        forecast.push({ month: month, forecast: Math.round(lastValue) });
    }

    return Promise.resolve(forecast);
}

export const createChat = (systemInstruction: string): Chat => {
  const ai = getAiClient();
  return ai.chats.create({
    model: 'gemini-2.5-flash',
    config: { systemInstruction },
  });
};

export const sendMessageToChat = async (chat: Chat, message: string): Promise<GenerateContentResponse> => {
  return await chat.sendMessage({ message });
};

export const generateImage = async (prompt: string): Promise<string | null> => {
  try {
    const ai = getAiClient();
    const response = await ai.models.generateImages({
      model: 'imagen-4.0-generate-001',
      prompt: prompt,
      config: { numberOfImages: 1, outputMimeType: 'image/jpeg', aspectRatio: '1:1' },
    });
    if (response.generatedImages && response.generatedImages.length > 0) {
      const base64ImageBytes = response.generatedImages[0].image.imageBytes;
      return `data:image/jpeg;base64,${base64ImageBytes}`;
    }
    return null;
  } catch (error) {
    console.error("Error generating image:", error);
    return null;
  }
};

export const editImage = async (base64Image: string, mimeType: string, prompt: string): Promise<string | null> => {
  try {
    const ai = getAiClient();
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: {
        parts: [
          { inlineData: { data: base64Image, mimeType } },
          { text: prompt },
        ],
      },
      config: { responseModalities: [Modality.IMAGE] },
    });
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        const base64ImageBytes: string = part.inlineData.data;
        return `data:${part.inlineData.mimeType};base64,${base64ImageBytes}`;
      }
    }
    return null;
  } catch (error) {
    console.error("Error editing image:", error);
    return null;
  }
};

export const generateVideo = async (base64Image: string, mimeType: string, prompt: string, aspectRatio: '16:9' | '9:16') => {
  // Veo requires a fresh client instance to pick up the latest key from the dialog
  const veoAi = new GoogleGenAI({ apiKey: process.env.API_KEY! });
  return await veoAi.models.generateVideos({
    model: 'veo-3.1-fast-generate-preview',
    prompt,
    image: { imageBytes: base64Image, mimeType },
    config: { numberOfVideos: 1, resolution: '720p', aspectRatio },
  });
};

export const pollVideoOperation = async (operation: any) => {
    const veoAi = new GoogleGenAI({ apiKey: process.env.API_KEY! });
    return await veoAi.operations.getVideosOperation({ operation });
};

export const groundedSearch = async (prompt: string): Promise<{ text: string, chunks: GroundingChunk[] }> => {
  try {
    const ai = getAiClient();
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: { tools: [{ googleSearch: {} }] },
    });
    const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks as GroundingChunk[] || [];
    return { text: response.text, chunks };
  } catch (error) {
    console.error("Error with grounded search:", error);
    return { text: "An error occurred during the search.", chunks: [] };
  }
};

export const groundedMapsSearch = async (prompt: string): Promise<{ text: string, chunks: GroundingChunk[] }> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject({ text: "Geolocation is not supported by your browser.", chunks: [] });
      return;
    }
    
    navigator.geolocation.getCurrentPosition(async (position) => {
      try {
        const { latitude, longitude } = position.coords;
        const ai = getAiClient();
        const response = await ai.models.generateContent({
          model: "gemini-2.5-flash",
          contents: prompt,
          config: {
            tools: [{ googleMaps: {} }],
            toolConfig: { retrievalConfig: { latLng: { latitude, longitude } } }
          },
        });
        const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks as GroundingChunk[] || [];
        resolve({ text: response.text, chunks });
      } catch (error) {
        console.error("Error with maps search:", error);
        reject({ text: "An error occurred during the maps search.", chunks: [] });
      }
    }, () => {
      reject({ text: "Unable to retrieve your location.", chunks: [] });
    });
  });
};

export const connectLive = (onMessage: (message: LiveServerMessage) => void, onError: (e: ErrorEvent) => void, onClose: (e: CloseEvent) => void, tools?: {functionDeclarations: FunctionDeclaration[]}[]) => {
  const ai = getAiClient();
  return ai.live.connect({
    model: 'gemini-2.5-flash-native-audio-preview-09-2025',
    callbacks: { onopen: () => {}, onmessage: onMessage, onerror: onError, onclose: onClose },
    config: {
      responseModalities: [Modality.AUDIO],
      speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Zephyr' } } },
      inputAudioTranscription: {},
      outputAudioTranscription: {},
      tools: tools
    }
  });
};