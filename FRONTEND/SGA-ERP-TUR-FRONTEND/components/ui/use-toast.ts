import { toast } from "react-hot-toast";

export const useToast = () => {
  return {
    toast: ({ title, description, variant }: { title: string; description?: string; variant?: string }) => {
      if (variant === 'destructive') {
        toast.error(`${title}${description ? `: ${description}` : ''}`);
      } else {
        toast.success(`${title}${description ? `: ${description}` : ''}`);
      }
    },
  };
};
