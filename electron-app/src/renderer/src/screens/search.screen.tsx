import { SubmitHandler } from 'react-hook-form'
import { useEffect, useState } from 'react'
import { ContextMenu, ContextMenuContent, ContextMenuItem, ContextMenuTrigger } from '@renderer/components/ui/context-menu'
import { Skeleton } from '@renderer/components/ui/skeleton'
import { FloatingSearchBar, SearchSchema } from '@renderer/components/floating-search-bar'


type ImageResponse = {
    path: string
    confidence?: number
}


export const SearchScreen = (): React.ReactElement => {
    const [imageResponses, setImageResponses] = useState<ImageResponse[] | null>(null);
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [selectedImages, setSelectedImages] = useState<string[]>([]);
    const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set());
    const [isFirstRender, setIsFirstRender] = useState<boolean>(true);


    const handleSearch = async (query: string, offset: number = 0): Promise<void> => {
        try {
            console.log('Offset:', offset)
            const imageResults = await window.api.queryImages(query, offset);
            if (imageResults) {
                const confidences = imageResults.distances[0];
                const updatedImageResponses = imageResults.metadatas[0].map((metadata, index) => ({
                    confidence: typeof confidences[index] === 'number' ? confidences[index] : 0,
                    path: metadata?.path as string || '',
                }))

                setImageResponses((current) => [...(current && searchQuery ? current : []), ...updatedImageResponses]);
            }
        } catch (err) {
            console.error("Error fetching image results:", err);
            throw Error('Error fetching image results: ' + err);
        }
    }

    const onSubmit: SubmitHandler<SearchSchema> = async (data) => {
        if (!data.query) return;
        setIsLoading(true);
        setSearchQuery(data.query);
        setImageResponses(null);

        try {
            await handleSearch(data.query);
        } catch (err) {
            console.error("Error fetching image results:", err);
            setImageResponses(null);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (event: KeyboardEvent): void => {
        setPressedKeys(prevKeys => {
            const newKeys = new Set(prevKeys);
            newKeys.add(event.key);
            return newKeys;
        });
    }

    const handleKeyUp = (event: KeyboardEvent): void => {
        setPressedKeys(prevKeys => {
            const newKeys = new Set(prevKeys);
            newKeys.delete(event.key);
            return newKeys;
        });
    }

    const getImages = async (offset: number = 0): Promise<void> => {
        console.log(offset)
        const images = await window.api.getImages(offset);
        if (images && images.metadatas) {
            const imageResponses = images.metadatas.map((metadata) => ({
                path: metadata?.path as string || '',
            }));
            setImageResponses(imageResponses);
        }
    }



    useEffect(() => {
        if (typeof window === 'undefined') return;
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);
        if (isFirstRender) {

            getImages()
            setIsFirstRender(false);
        }



        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [isFirstRender])

    // useEffect(() => {
    //     const handleScroll = (): void => {
    //         const scrollPosition = window.innerHeight + window.scrollY;
    //         const threshold = document.body.offsetHeight;
    //         if (scrollPosition >= threshold - 2) {
    //             console.log('running')
    //             if (!searchQuery) {
    //                 // Load more images when scrolled to bottom
    //                 getImages(imageResponses ? imageResponses.length : 0);
    //             } else {
    //                 console.log('hi')
    //                 handleSearch(searchQuery, imageResponses ? imageResponses.length : 0);
    //             }
    //         }
    //     };
    //     window.addEventListener('scroll', handleScroll);

    //     return () => {
    //         window.removeEventListener('scroll', handleScroll);
    //     };
    // }, [imageResponses, searchQuery]) // Reattach scroll listener when these change

    return <div className="p-8 pb-24">
        {searchQuery && <div className="text-gray-600 mb-4">Showing results for &quot;<span className="font-semibold">{searchQuery}</span>&quot;</div>}
        {imageResponses && imageResponses.length > 0 && (
            <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] items-center gap-4">
                {imageResponses.map((response, index) => (
                    <div key={index} className={`ring-2 ${selectedImages.includes(response.path) ? 'ring-blue-500' : 'ring-transparent'}`} onClick={() => {
                        if (pressedKeys.has('Meta')) {
                            if (selectedImages.includes(response.path)) {
                                setSelectedImages(selectedImages.filter(img => img !== response.path));
                            } else {
                                setSelectedImages([...selectedImages, response.path]);
                            }
                        }

                    }}>
                        <ContextMenu>
                            <ContextMenuTrigger className="block w-full h-auto border rounded overflow-hidden relative aspect-square">
                                {response.path ? (
                                    <img src={`media://${response.path}`} alt={`Result ${index + 1}`} className="w-full h-full object-contain absolute inset-0" />
                                ) : (
                                    <div className="w-full h-32 flex items-center justify-center bg-gray-200">Image not found</div>
                                )}

                            </ContextMenuTrigger>
                            <ContextMenuContent>
                                <ContextMenuItem onClick={() => window.api.openFiles(selectedImages.length > 0 ? selectedImages : [response.path])}>Open {selectedImages.length > 1 ? 'Images' : 'Image'}</ContextMenuItem>
                                <ContextMenuItem onClick={async () => {
                                    console.log(response.path)
                                    if (response.path && typeof response.path === 'string' && response.path.trim() !== '') {
                                        const showFileResponse = await window.api.showFile(response.path);
                                        console.log(showFileResponse)
                                    } else {
                                        window.alert('File path is invalid or missing.');
                                    }
                                }}>Show Image in Finder</ContextMenuItem>
                            </ContextMenuContent>
                        </ContextMenu>
                        {response.confidence && <span className="text-xs text-gray-500">Confidence: {response.confidence.toFixed(4)}</span>}

                    </div>
                ))}
            </div>
        )}
        {!imageResponses && isLoading && (
            <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4">
                {Array.from({ length: 9 }).map((_, index) => (
                    <Skeleton key={index} className="w-full h-auto aspect-square rounded border" />
                ))}
            </div>
        )}
        <FloatingSearchBar onSearch={onSubmit} />
    </div>;
}
