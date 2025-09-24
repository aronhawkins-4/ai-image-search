

import { useEffect, useState } from "react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion";
import { Folder, Image } from "lucide-react";
import { Button } from "./ui/button";

const getDirectory = async (path: string): Promise<{ name: string; type: string, targetDir: string }[]> => {
    const response = await window.api.getDirectory(path)
    return response
}
const openFile = async (path: string): Promise<{ message: string, paths: string[] }> => {
    const response = await window.api.openFiles([path])
    return response;
}

interface DirectoryAccordionItemProps {
    path: string;
    // isIndexible: boolean
}

export const DirectoryAccordionItem: React.FC<DirectoryAccordionItemProps> = ({ path }) => {
    const [contents, setContents] = useState<{ name: string; type: string, targetDir: string }[]>([]);
    // const [hasImages, setHasImages] = useState(false)

    useEffect(() => {
        getDirectory(path).then(setContents);
    }, [path]);

    // useEffect(() => {
    //     if (contents) {
    //         const validImageTypes = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
    //         for (const entry of contents) {
    //             if (validImageTypes.includes(entry.name.substring(entry.name.lastIndexOf('.')))) {
    //                 setHasImages(true)
    //                 return;
    //             }
    //         }
    //     }
    // }, [contents])

    return (

        <AccordionItem key={path || 'Home'} value={path || 'Home'} className="">
            <AccordionTrigger className="bg-muted px-4"><div className="flex items-center gap-2 flex-1"><Folder className="w-4" />{path ? path.substring(path.lastIndexOf('/') + 1) : 'Home'}
                {/* {hasImages ? <Download className="w-4 ml-auto" /> : null} */}
            </div></AccordionTrigger>
            <AccordionContent className="pl-4 border-l border-gray-300 pt-2 pb-0">
                <Accordion type="single" collapsible className="space-y-2">
                    {contents.map((entry) => {
                        const fileType = entry.name.substring(entry.name.lastIndexOf('.'));
                        let FileIcon;
                        switch (fileType) {
                            case '.jpg':
                            case '.jpeg':
                            case '.png':
                            case '.webp':
                            case '.avif':
                                FileIcon = Image;
                                break;
                            // case '.js':
                            // case '.ts':
                            // case '.py':
                            // case '.go':
                            // case '.html':
                            // case '.json':
                            // case '.css':
                            //     FileIcon = Code;
                            //     break;
                            // default:
                            //     FileIcon = File;

                        }
                        return <div key={entry.name}>
                            {entry.type === 'directory' ? (
                                <DirectoryAccordionItem
                                    path={path + `/${entry.name}`}

                                />
                            ) : <Button className="py-4 flex items-center gap-2 w-full justify-start" variant="ghost" onClick={() => openFile(path + `/${entry.name}`)}><FileIcon className="w-4" />{entry.name}</Button>}
                        </div>
                    })}
                </Accordion>
            </AccordionContent>
        </AccordionItem>
    );
};
