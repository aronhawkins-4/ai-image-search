
import { Route } from 'react-router-dom'
import { JSX } from 'react'
import { Router } from '@lib/electron-router-dom'
import { Layout } from './layout'
import { HomeScreen } from './screens/home.screen'
import { SearchScreen } from './screens/search.screen'

export default function Routes(): JSX.Element {
    return <Router
        main={
            <Route path="/" element={<Layout />}>
                <Route path="/" element={<HomeScreen />} />
                <Route path="/search" element={<SearchScreen />} />
            </Route>
        }
    />
}
