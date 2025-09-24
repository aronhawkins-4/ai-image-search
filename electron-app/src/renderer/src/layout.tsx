import { JSX } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { Separator } from '@renderer/components/ui/separator'




export function Layout(): JSX.Element {
    return (
        <main className="flex flex-col items-center gap-5">
            <nav className="flex w-full items-stretch gap-2 p-4 border-b">
                <NavLink to="/">Home</NavLink>

                <Separator orientation="vertical" className='h-auto!' />

                <NavLink to="/search">Search</NavLink>
            </nav>

            <section className="w-full">
                <Outlet />
            </section>

        </main>
    )
}