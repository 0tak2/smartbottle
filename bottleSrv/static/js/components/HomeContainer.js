import axios from 'https://unpkg.com/axios@1.2.0/dist/esm/axios.js'
import { ref, reactive } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import HomeCard from './HomeCard.js'

const hydr_url = '/api/hydration/last'
const tds_url = '/api/tds'

export default {
    components: {
        HomeCard
    },
    setup() {
        const loadedData = ref(0)
        const isLoading = ref(true)
        const latestData = reactive({
            hydration: null,
            tds: null
        })

        async function fetchHydrData() {
            isLoading.value = true

            try {
                const response = await axios.get(hydr_url)
                latestData.hydration = response.data.result
            } catch (error) {
                console.error(error)
            }

            loadedData.value++
            if (loadedData.value === 2) {
                isLoading.value = false
                loadedData.value = 0
            }
        }

        async function fetchTdsData() {
            isLoading.value = true

            try {
                const response = await axios.get(tds_url + '?size=1&page=0')
                latestData.tds = response.data.result[0]
            } catch (error) {
                console.error(error)
            }

            loadedData.value++
            if (loadedData.value === 2) {
                isLoading.value = false
                loadedData.value = 0
            }
        }

        fetchHydrData()
        fetchTdsData()

        return {
            loadedData,
            isLoading,
            latestData,
            fetchHydrData,
            fetchTdsData
        }
    },
    template: `
        <h1>홈</h1>
        <div v-if="!isLoading" class="full-width">
            <home-card
                v-bind:value_volumeDiffer="latestData.hydration.value_differ"
                v-bind:value_tds="latestData.tds.value_tds"
                v-bind:created_hydrationData="latestData.hydration.created"
                v-bind:created_tdsData="latestData.tds.created">
            </home-card>
            <div class="home-refresh-btn-wrapper">
                <button v-on:click="() => {
                    fetchHydrData()
                    fetchTdsData()}">
                        새로고침
                </button>
            </div>
        </div>
        <div v-else class="loading">
            로딩중
        </div>
    `
}