
import React, { createContext, useContext, useState, useCallback, useMemo, useEffect, PropsWithChildren } from 'react';
import { createDefaultFunnel } from '../components/funnel-builder/data';
import type { Funnel, Block, LandingPage, Categoria, Subcategoria, CadenaTurismo, Asset } from '../types';

type AllData = {
    cadenas: CadenaTurismo[];
    categorias: Categoria[];
    subcategorias: Subcategoria[];
    landingPages: LandingPage[];
    mediaLibrary: Asset[];
};

function useHistoryState<T>(initialState: T) {
    const [history, setHistory] = useState([initialState]);
    const [pointer, setPointer] = useState(0);
    const state = history[pointer];
    const setState = useCallback((newState: T | ((prevState: T) => T), fromHistory = false) => {
        const resolvedState = typeof newState === 'function' ? (newState as (prevState: T) => T)(state) : newState;
        if (!fromHistory && JSON.stringify(resolvedState) === JSON.stringify(state)) return;
        const newHistory = history.slice(0, pointer + 1);
        newHistory.push(resolvedState);
        setHistory(newHistory);
        setPointer(newHistory.length - 1);
    }, [history, pointer, state]);
    const undo = useCallback(() => { if (pointer > 0) setPointer(p => p - 1); }, [pointer]);
    const redo = useCallback(() => { if (pointer < history.length - 1) setPointer(p => p + 1); }, [pointer, history.length]);
    return { state, setState, undo, redo, canUndo: pointer > 0, canRedo: pointer < history.length - 1 };
}

interface FunnelBuilderContextType {
    allData: AllData;
    updateData: (updater: (draft: AllData) => void | any) => void;
    undo: () => void;
    redo: () => void;
    canUndo: boolean;
    canRedo: boolean;
    saveStatus: 'saved' | 'saving' | 'error';
    activeCadenaId: string | null;
    setActiveCadenaId: (id: string | null) => void;
    activeCategoriaId: string | null;
    setActiveCategoriaId: (id: string | null) => void;
    activeSubcategoriaId: string | null;
    setActiveSubcategoriaId: (id: string | null) => void;
    activeLandingPageId: string | null;
    setActiveLandingPageId: (id: string | null) => void;
    activeFunnelId: string | null;
    setActiveFunnelId: (id: string | null) => void;
    activePageId: string | null;
    setActivePageId: (id: string | null) => void;
    activeBlockId: string | null;
    setActiveBlockId: (id: string | null) => void;
    activeCadena: CadenaTurismo | undefined;
    activeLandingPage: LandingPage | undefined;
    activeFunnel: Funnel | undefined;
    activePage: any | undefined;
    activeBlock: Block | undefined;
    filteredCategorias: Categoria[];
    filteredSubcategorias: Subcategoria[];
    filteredLandingPages: LandingPage[];
    isCreateFunnelModalOpen: boolean;
    setIsCreateFunnelModalOpen: (isOpen: boolean) => void;
    isMediaLibraryOpen: boolean;
    setIsMediaLibraryOpen: (isOpen: boolean) => void;
    mediaLibraryCallback: ((url: string) => void) | null;
    setMediaLibraryCallback: (cb: ((url: string) => void) | null) => void;
    activeBreakpoint: 'desktop' | 'tablet' | 'mobile';
    setActiveBreakpoint: (bp: 'desktop' | 'tablet' | 'mobile') => void;
    handleCreateFunnel: (name: string) => void;
}

const FunnelBuilderContext = createContext<FunnelBuilderContextType | undefined>(undefined);

interface FunnelBuilderProviderProps {
  authToken: string;
}

export const FunnelBuilderProvider: React.FC<PropsWithChildren<FunnelBuilderProviderProps>> = ({ children, authToken }) => {
    const { state: allData, setState: setAllData, undo, redo, canUndo, canRedo } = useHistoryState<AllData | null>(null);
    const [activeCadenaId, setActiveCadenaId] = useState<string | null>(null);
    const [activeCategoriaId, setActiveCategoriaId] = useState<string | null>(null);
    const [activeSubcategoriaId, setActiveSubcategoriaId] = useState<string | null>(null);
    const [activeLandingPageId, setActiveLandingPageId] = useState<string | null>(null);
    const [activeFunnelId, setActiveFunnelId] = useState<string | null>(null);
    const [activePageId, setActivePageId] = useState<string | null>(null);
    const [activeBlockId, setActiveBlockId] = useState<string | null>(null);
    const [isCreateFunnelModalOpen, setIsCreateFunnelModalOpen] = useState(false);
    const [isMediaLibraryOpen, setIsMediaLibraryOpen] = useState(false);
    const [mediaLibraryCallback, setMediaLibraryCallback] = useState<((url: string) => void) | null>(null);
    const [activeBreakpoint, setActiveBreakpoint] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
    const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!authToken) return;
            try {
                const response = await fetch('/api/bff/funnel-builder/funnel-editor-data/', {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                if (!response.ok) throw new Error('El sistema no pudo recuperar los datos del constructor. Verifique su conexión activa.');
                const data = await response.json();
                setAllData(data);
            } catch (error) {
                console.error("Failed to fetch funnel data:", error);
                setSaveStatus('error');
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, [authToken, setAllData]);

    const saveFunnel = useCallback(async (funnelToSave: Funnel) => {
        setSaveStatus('saving');
        try {
            const response = await fetch(`/api/bff/funnel-builder/funnels/${funnelToSave.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(funnelToSave)
            });
            if (!response.ok) throw new Error('Failed to save funnel');
            setTimeout(() => setSaveStatus('saved'), 1000);
        } catch (error) {
            console.error("Error saving funnel:", error);
            setSaveStatus('error');
        }
    }, [authToken]);

    const updateData = (updater: (draft: AllData) => void | any) => {
        if (!allData) return;
        const newState = JSON.parse(JSON.stringify(allData));
        updater(newState);
        setAllData(newState);

        const activeLp = newState.landingPages.find(lp => lp.id === activeLandingPageId);
        const activeF = activeLp?.funnels.find(f => f.id === activeFunnelId);
        if (activeF) {
            saveFunnel(activeF);
        }
    };

    useEffect(() => {
        if (allData && allData.cadenas.length > 0 && !activeCadenaId) {
            const cadenaToLoad = allData.cadenas[0]!;
            const catToLoad = allData.categorias.find(c => String(c.cadenaId) === String(cadenaToLoad.id));
            const subToLoad = catToLoad ? allData.subcategorias.find(s => String(s.categoriaId) === String(catToLoad.id)) : undefined;
            const lpToLoad = subToLoad ? allData.landingPages.find(l => String(l.subcategoriaId) === String(subToLoad.id)) : undefined;
            const funnelToLoad = lpToLoad?.funnels[0];

            setActiveCadenaId(String(cadenaToLoad.id));
            if (catToLoad) setActiveCategoriaId(String(catToLoad.id));
            if (subToLoad) setActiveSubcategoriaId(String(subToLoad.id));
            if (lpToLoad) setActiveLandingPageId(String(lpToLoad.id));
            if (funnelToLoad) {
                setActiveFunnelId(String(funnelToLoad.id));
                setActivePageId(funnelToLoad.pages[0]?.id || null);
            }
        }
    }, [allData, activeCadenaId]);

    const activeCadena = useMemo(() => allData?.cadenas.find(c => String(c.id) === activeCadenaId), [allData, activeCadenaId]);
    const filteredCategorias = useMemo(() => allData?.categorias.filter(c => String(c.cadenaId) === activeCadenaId) || [], [allData, activeCadenaId]);
    const filteredSubcategorias = useMemo(() => activeCategoriaId ? allData?.subcategorias.filter(s => String(s.categoriaId) === activeCategoriaId) : [], [allData, activeCategoriaId]);
    const filteredLandingPages = useMemo(() => activeSubcategoriaId ? allData?.landingPages.filter(lp => String(lp.subcategoriaId) === activeSubcategoriaId) : [], [allData, activeSubcategoriaId]);
    const activeLandingPage = useMemo(() => allData?.landingPages.find(lp => String(lp.id) === activeLandingPageId), [allData, activeLandingPageId]);
    const activeFunnel = useMemo(() => activeLandingPage?.funnels.find(f => String(f.id) === activeFunnelId), [activeLandingPage, activeFunnelId]);
    const activePage = useMemo(() => activeFunnel?.pages.find(p => p.id === activePageId), [activeFunnel, activePageId]);
    const activeBlock = useMemo(() => activePage?.blocks.find(b => b.id === activeBlockId), [activePage, activeBlockId]);

    const handleCreateFunnel = async (newFunnelName: string) => {
        if (!newFunnelName.trim() || !activeLandingPageId || !allData) return;

        const newFunnelScaffold = createDefaultFunnel(activeLandingPageId, newFunnelName);

        try {
            const response = await fetch(`/api/bff/funnel-builder/landing-pages/${activeLandingPageId}/funnels/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: newFunnelScaffold.name,
                    schema: newFunnelScaffold
                })
            });

            if (!response.ok) throw new Error('Failed to create funnel');

            const createdFunnel = await response.json();

            const updater = (draft: AllData) => {
                const lp = draft.landingPages.find(l => l.id === activeLandingPageId);
                if (lp) {
                    lp.funnels.push(createdFunnel);
                }
            };

            const newState = JSON.parse(JSON.stringify(allData));
            updater(newState);
            setAllData(newState);

            setActiveFunnelId(String(createdFunnel.id));
            setActivePageId(createdFunnel.pages[0]?.id || null);

        } catch (error) {
            console.error("Error creating funnel:", error);
            setSaveStatus('error');
        } finally {
            setIsCreateFunnelModalOpen(false);
        }
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    const value: FunnelBuilderContextType = {
        allData: allData!,
        updateData, undo, redo, canUndo, canRedo, saveStatus,
        activeCadenaId, setActiveCadenaId,
        activeCategoriaId, setActiveCategoriaId,
        activeSubcategoriaId, setActiveSubcategoriaId,
        activeLandingPageId, setActiveLandingPageId,
        activeFunnelId, setActiveFunnelId,
        activePageId, setActivePageId,
        activeBlockId, setActiveBlockId,
        activeCadena, activeLandingPage, activeFunnel, activePage, activeBlock,
        filteredCategorias, filteredSubcategorias, filteredLandingPages,
        isCreateFunnelModalOpen, setIsCreateFunnelModalOpen,
        isMediaLibraryOpen, setIsMediaLibraryOpen,
        mediaLibraryCallback, setMediaLibraryCallback,
        activeBreakpoint, setActiveBreakpoint,
        handleCreateFunnel
    };

    return <FunnelBuilderContext.Provider value={value}>{children}</FunnelBuilderContext.Provider>;
};

export const useFunnelBuilder = () => {
    const context = useContext(FunnelBuilderContext);
    if (context === undefined) {
        throw new Error('useFunlBuilder must be used within a FunnelBuilderProvider');
    }
    return context;
};
