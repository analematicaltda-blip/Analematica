import React from 'react';
import { FacebookIcon, InstagramIcon, TikTokIcon, YouTubeIcon, XIcon, PostIcon, StoryIcon, ReelIcon } from './icons';

export type PlatformID = 'facebook' | 'instagram' | 'tiktok' | 'youtube' | 'x';
export type SelectedPlatforms = { [key in PlatformID]?: string[] };

interface Format {
    id: string;
    name: string;
    icon: React.FC<{className?: string}>;
}

const platformFormats: { [key in PlatformID]: Format[] } = {
    facebook: [
        { id: 'post', name: 'Post', icon: PostIcon },
        { id: 'story', name: 'Story', icon: StoryIcon },
        { id: 'reel', name: 'Reel', icon: ReelIcon },
    ],
    instagram: [
        { id: 'post', name: 'Post', icon: PostIcon },
        { id: 'story', name: 'Story', icon: StoryIcon },
        { id: 'reel', name: 'Reel', icon: ReelIcon },
    ],
    tiktok: [
        { id: 'video', name: 'Video', icon: ReelIcon },
    ],
    youtube: [
        { id: 'video', name: 'Video', icon: PostIcon },
        { id: 'short', name: 'Short', icon: ReelIcon },
    ],
    x: [
        { id: 'post', name: 'Post', icon: PostIcon },
    ],
};

const socialPlatforms: { id: PlatformID, name: string, icon: React.FC<{className?: string}> }[] = [
    { id: 'facebook', name: 'Facebook', icon: FacebookIcon },
    { id: 'instagram', name: 'Instagram', icon: InstagramIcon },
    { id: 'tiktok', name: 'TikTok', icon: TikTokIcon },
    { id: 'youtube', name: 'YouTube', icon: YouTubeIcon },
    { id: 'x', name: 'X', icon: XIcon },
];


interface PlatformFormatSelectorProps {
    selected: SelectedPlatforms;
    onSelectionChange: (selection: SelectedPlatforms) => void;
}

const PlatformFormatSelector: React.FC<PlatformFormatSelectorProps> = ({ selected, onSelectionChange }) => {
    
    const togglePlatform = (platformId: PlatformID) => {
        const newSelection = { ...selected };
        if (newSelection[platformId]) {
            delete newSelection[platformId];
        } else {
            // Select the first format by default
            newSelection[platformId] = [platformFormats[platformId][0].id];
        }
        onSelectionChange(newSelection);
    };

    const toggleFormat = (platformId: PlatformID, formatId: string) => {
        const newSelection = { ...selected };
        const currentFormats = newSelection[platformId] || [];
        const isSingleFormatPlatform = platformFormats[platformId].length === 1;

        if (currentFormats.includes(formatId)) {
            // If it's the last one selected, remove the platform entirely
            if (currentFormats.length === 1) {
                 delete newSelection[platformId];
            } else {
                 newSelection[platformId] = currentFormats.filter(f => f !== formatId);
            }
        } else {
            // For single-format platforms, this replaces the selection. For others, it adds.
            newSelection[platformId] = isSingleFormatPlatform ? [formatId] : [...currentFormats, formatId];
        }
        onSelectionChange(newSelection);
    };

    return (
        <div className="space-y-4">
            <h4 className="text-md font-semibold text-foreground">Distribuir en Redes y Formatos</h4>
            {socialPlatforms.map(platform => (
                <div key={platform.id} className="p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                        <button
                            type="button"
                            onClick={() => togglePlatform(platform.id)}
                            className={`flex items-center space-x-2 p-2 rounded-lg border-2 transition-colors duration-200 ${
                                selected[platform.id]
                                    ? 'bg-primary text-primary-foreground border-primary/80'
                                    : 'bg-muted border-border text-muted-foreground hover:bg-accent'
                            }`}
                            title={platform.name}
                        >
                            <platform.icon className="w-5 h-5" />
                        </button>
                         <span className={`font-semibold ${selected[platform.id] ? 'text-foreground' : 'text-muted-foreground'}`}>{platform.name}</span>
                    </div>

                    {selected[platform.id] && platformFormats[platform.id].length > 1 && (
                         <div className="flex flex-wrap gap-2 mt-3 pl-2">
                             {platformFormats[platform.id].map(format => (
                                 <button
                                     key={format.id}
                                     type="button"
                                     onClick={() => toggleFormat(platform.id, format.id)}
                                     className={`flex items-center space-x-1.5 text-xs px-2 py-1 rounded-md transition-colors duration-200 ${
                                         selected[platform.id]?.includes(format.id)
                                             ? 'bg-primary text-primary-foreground'
                                             : 'bg-muted text-muted-foreground hover:bg-accent'
                                     }`}
                                 >
                                     <format.icon className="w-4 h-4" />
                                     <span>{format.name}</span>
                                 </button>
                             ))}
                         </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default PlatformFormatSelector;