
import { useForm, SubmitHandler } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
    Form,
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
} from "@renderer/components/ui/form";
import { Button } from "../components/ui/button";

const searchSchema = z.object({
    query: z.string().min(1, "Please enter a search term"),
});

export type SearchSchema = z.infer<typeof searchSchema>;

export function FloatingSearchBar({ onSearch }: { onSearch: (data: SearchSchema) => void }): React.ReactElement {
    const form = useForm<SearchSchema>({
        resolver: zodResolver(searchSchema),
        defaultValues: { query: "" },
    });

    const handleSubmit: SubmitHandler<SearchSchema> = (data) => {
        onSearch(data);
        form.reset();
    };

    return (
        <div
            className="fixed bottom-4 left-0 right-0 mx-auto z-[1000] max-w-xl w-[90%] shadow-lg rounded-xl bg-white p-4 flex items-center"
        >
            <Form {...form}>
                <form
                    onSubmit={form.handleSubmit(handleSubmit)}
                    className="w-full flex items-end gap-2"
                >
                    <FormField
                        control={form.control}
                        name="query"
                        render={({ field }) => (
                            <FormItem className="flex-1">
                                <FormLabel className="sr-only">Search</FormLabel>
                                <FormControl>
                                    <input
                                        {...field}
                                        placeholder="Search images..."
                                        className="w-full px-3 py-2 rounded-lg border border-gray-200 text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" className="h-10">
                        Search
                    </Button>
                </form>
            </Form>
        </div>
    );
}
