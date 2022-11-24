import { createApp, ref } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import NavBar from './components/NavBar.js'
import HomeContainer from './components/HomeContainer.js'
import HydrationContainer from './components/HydrationContainer.js'
import TdsContainer from './components/TdsContainer.js'

const features = {
    HOME: 'home',
    HYDR: 'hydration',
    TDS: 'tds'
}

createApp({
    components: {
        NavBar,
        HomeContainer,
        HydrationContainer,
        TdsContainer
    },
    setup() {
        const activeFeature = ref(features.HOME)

        return {
            activeFeature,
            features
        }
    },
    template: `
        <div class="container">
            <nav-bar
                v-bind:features="features"
                v-on:selected="(feature) => activeFeature = feature">
            </nav-bar>
            <home-container v-if="activeFeature === features.HOME"></home-container>
            <hydration-container v-if="activeFeature === features.HYDR"></hydration-container>
            <tds-container v-if="activeFeature === features.TDS"></tds-container>
        </div>
    `
}).mount('#app')