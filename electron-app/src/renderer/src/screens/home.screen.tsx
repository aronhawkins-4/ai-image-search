import { DirectoryAccordionItem } from "@renderer/components/directory-accordion-item";
import { Accordion } from "@renderer/components/ui/accordion";
import React from "react";

export function HomeScreen(): React.ReactElement {
    return (
        <div className="p-8 pb-24">
            <Accordion type="single" collapsible>
                <DirectoryAccordionItem path="" />
            </Accordion>
        </div>


    )
}