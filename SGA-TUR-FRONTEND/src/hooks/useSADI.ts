'use client';

import { useState, useCallback, useRef } from 'react';
import { SADIState } from '../ui/components/feedback/SADIVoiceLayer';
import { voiceEndpoints } from '@/services/endpoints/voice';
import { useGRC } from '@/contexts/GRCContext';
import { usePermissions } from '@/ui/guards/PermissionGuard';
import { auditLogger } from '@/services/auditLogger';
import httpClient from '@/services/httpClient';

export function useSADI() {
  const [state, setState] = useState<SADIState>('idle');
  const [responseMessage, setResponseMessage] = useState<string>('');
  const [lastIntent, setLastIntent] = useState<any>(null);
  const [confirmationData, setConfirmationData] = useState<{ message: string, actionId: string, intent?: string } | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const { evaluateVoiceAction } = useGRC();
  const { role } = usePermissions();

  const pollMission = useCallback(async (missionId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const res = await voiceEndpoints.getMissionStatus(missionId);
        const { estado, reporte_final } = res.data;

        if (estado === 'COMPLETADA' || estado === 'FALLIDA') {
          if (pollingRef.current) clearInterval(pollingRef.current);
          setResponseMessage(reporte_final || `Misión terminada con estado: ${estado}`);
          setState(estado === 'COMPLETADA' ? 'success' : 'error');

          auditLogger.log({
            type: 'ACTION_PERMITTED',
            view: 'Voice SADI',
            action: `Mission ${missionId} finished`,
            details: { status: estado },
            userRole: role,
            status: estado === 'COMPLETADA' ? 'OK' : 'ERROR'
          });

          setTimeout(() => setState('idle'), 5000);
        }
      } catch (err) {
        if (pollingRef.current) clearInterval(pollingRef.current);
        setState('error');
      }
    }, 2000);
  }, [role]);

  const processAudio = useCallback(async (audioBlob: Blob) => {
    setState('processing');
    setResponseMessage('');

    try {
      const response = await voiceEndpoints.sendAudio(audioBlob);
      const { text, audio_url, intent, requires_confirmation, confirmation_message, action_id, mission_id } = response.data;

      setResponseMessage(text);
      setLastIntent(intent);

      // GRC VALIDATION (F-E)
      const evaluation = evaluateVoiceAction(intent, role);

      auditLogger.log({
        type: 'VOICE_INTENT_DETECTED',
        view: 'Voice SADI',
        action: `Intent: ${intent}`,
        details: { transcription: text, evaluation },
        userRole: role,
        status: evaluation.permitted ? 'OK' : 'WARN'
      });

      if (!evaluation.permitted) {
        setState('error');
        setResponseMessage(`ACCIÓN DENEGADA: ${evaluation.reason}`);
        // TTS Playback for error
        return;
      }

      if (requires_confirmation || evaluation.requiresConfirmation) {
          setConfirmationData({
            message: confirmation_message || `¿Confirmas la ejecución de '${intent}' con nivel de riesgo ${evaluation.risk}?`,
            actionId: action_id,
            intent: intent
          });
          setState('confirming');
      } else if (mission_id) {
          setState('processing');
          pollMission(mission_id);
      } else {
          setState('success');
          setTimeout(() => setState('idle'), 5000);
      }

      // TTS Playback
      if (audio_url) {
        const audio = new Audio(audio_url);
        audio.play();
      }

    } catch (err) {
      console.error("SADI processing error", err);
      setState('error');
      setResponseMessage("No pude comprender la instrucción o el servicio no está disponible.");

      setTimeout(() => {
        setState('idle');
      }, 5000);
    }
  }, [evaluateVoiceAction, role, pollMission]);

  const sendTextIntent = useCallback(async (text: string) => {
    setState('processing');
    try {
        const response = await voiceEndpoints.sendIntent(text);
        const { text: responseText, intent } = response.data;

        const evaluation = evaluateVoiceAction(intent, role);
        if (!evaluation.permitted) {
            setState('error');
            setResponseMessage(`BLOQUEO GRC: ${evaluation.reason}`);
            return;
        }

        setResponseMessage(responseText);
        setLastIntent(intent);
        setState('success');
        setTimeout(() => setState('idle'), 5000);
    } catch (err) {
        setState('error');
        setResponseMessage("Error de conexión con el motor SADI.");
        setTimeout(() => setState('idle'), 5000);
    }
  }, [evaluateVoiceAction, role]);

  const confirmAction = useCallback(async () => {
    if (!confirmationData) return;
    setState('processing');
    try {
        // En un entorno real, actionId vendría del backend para asegurar trazabilidad
        if (confirmationData.actionId) {
            await httpClient.post(`/api/voice/actions/${confirmationData.actionId}/confirm/`);
        }

        auditLogger.log({
            type: 'VOICE_ACTION_CONFIRMED',
            view: 'Voice SADI',
            action: `Confirmed: ${confirmationData.intent}`,
            userRole: role,
            status: 'OK'
        });

        setState('success');
        setResponseMessage("Acción confirmada verbalmente y ejecutada por el Kernel.");
        setConfirmationData(null);
        setTimeout(() => setState('idle'), 5000);
    } catch (err) {
        setState('error');
        setResponseMessage("Error al procesar la confirmación en el Kernel.");
        auditLogger.log({
            type: 'ACTION_DENIED',
            view: 'Voice SADI',
            action: `Voice Confirmation FAILED: ${confirmationData.intent}`,
            userRole: role,
            status: 'ERROR'
        });
    }
  }, [confirmationData, role]);

  const cancelAction = useCallback(() => {
    auditLogger.log({
        type: 'VOICE_ACTION_ABORTED',
        view: 'Voice SADI',
        action: `Aborted: ${confirmationData?.intent}`,
        userRole: role,
        status: 'INFO'
    });
    setConfirmationData(null);
    setState('idle');
    setResponseMessage("Operación abortada por el usuario.");
  }, [confirmationData, role]);

  return {
    state,
    responseMessage,
    lastIntent,
    confirmationData,
    processAudio,
    sendTextIntent,
    confirmAction,
    cancelAction,
    setState
  };
}
