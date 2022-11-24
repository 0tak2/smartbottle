import axios from 'https://unpkg.com/axios@1.2.0/dist/esm/axios.js'
import { ref, reactive, watch } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import HydrationDataTable from './HydrationDataTable.js'

const hydrBaseUrl = '/api/hydration'

export default {
    components: {
        HydrationDataTable
    },
    setup() {
        const isLoading = ref(true)

        const isLastPage = ref(false)

        const query = reactive({
            page: 0,
            dateOption: {
                active: false,
                startDate: getTodayStr(),
                startTime: '00:00',
                endDate: getTodayStr(),
                endTime: '23:59',
            }
        })

        const fetchedData = reactive({
            hydration: null,
        })

        function getTodayStr() {
            const date = new Date()

			var year = date.getFullYear();
            var month = date.getMonth() + 1;
            var day = date.getDate();

            return `${year.toString()}-${month.toString()}-${day.toString()}`
        }

        function handlePageDecrement() {
            if (query.page > 0) {
                --query.page
            }
        }

        function handlePageIncrement() {
            if (!isLastPage.value) {
                ++query.page
            }
        }

        async function handleExport() {
            let requestUrl
            if (query.dateOption.active) {
                const { active, startDate, startTime, endDate, endTime } = query.dateOption
                const start = startDate + ' ' + startTime + ":00"
                const end = endDate + ' ' + endTime + ":00"
                requestUrl = `${hydrBaseUrl}?size=10&page=${query.page}&start_time=${start}&end_time=${end}`
            } else {
                requestUrl = `${hydrBaseUrl}?size=10&page=${query.page}`
            }

            try {
                const response = await axios.get(requestUrl + '&export')
                window.open(response.data.result.url)
            } catch (error) {
                console.error(error)
            }
        }

        async function fetchHydrData() {
            isLoading.value = true

            let requestUrl
            if (query.dateOption.active) {
                const { active, startDate, startTime, endDate, endTime } = query.dateOption
                const start = startDate + ' ' + startTime + ":00"
                const end = endDate + ' ' + endTime + ":00"
                requestUrl = `${hydrBaseUrl}?size=10&page=${query.page}&start_time=${start}&end_time=${end}`
            } else {
                requestUrl = `${hydrBaseUrl}?size=10&page=${query.page}`
            }

            try {
                const response = await axios.get(requestUrl)
                fetchedData.hydration = response.data.result
            } catch (error) {
                console.error(error)
            }

            if (fetchedData.hydration.length === 0) {
                isLastPage.value = true
            } else {
                isLastPage.value = false
            }

            isLoading.value = false
        }
        
        watch(query, fetchHydrData)

        fetchHydrData()

        return {
            isLoading,
            query,
            fetchedData,
            fetchHydrData,
            handlePageDecrement,
            handlePageIncrement,
            handleExport
        }
    },
    template: `
        <h1>부피 데이터 상세 조회</h1>
        <div v-if="!isLoading" class="full-width">
            <hydration-data-table v-bind:hydrationData="fetchedData.hydration"></hydration-data-table>
            <button class="export-btn" v-on:click="handleExport">엑셀 파일로 내보내기</button>
        </div>
        <div v-else class="loading">
            로딩중
        </div>
        <div class="page-control-wrapper">
            <button v-on:click="handlePageDecrement">
                &nbsp&lt&nbsp
            </button>
            <span class="page-control-indicator">&nbsp&nbsp현재 {{query.page + 1}}페이지&nbsp&nbsp</span>
            <button v-on:click="handlePageIncrement">
                &nbsp&gt&nbsp
            </button>
        </div>
        <div class="date-control-wrapper">
            <input type="checkbox" v-model="query.dateOption.active">시간별 조회<br />
            <input type="date" class="date-control-input" v-model="query.dateOption.startDate" v-bind:disabled="!query.dateOption.active">
            <input type="time" class="date-control-input" v-model="query.dateOption.startTime" v-bind:disabled="!query.dateOption.active"> 부터<br />
            <input type="date" class="date-control-input" v-model="query.dateOption.endDate" v-bind:disabled="!query.dateOption.active">
            <input type="time" class="date-control-input" v-model="query.dateOption.endTime" v-bind:disabled="!query.dateOption.active"> 까지<br />
        </div>
    `
}