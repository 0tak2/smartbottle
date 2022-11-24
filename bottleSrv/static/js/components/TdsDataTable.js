import { computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

export default {
    props: [
        'tdsData'
    ],
    setup(props) {
        const { tdsData } = props
        
        const isLast = computed(() => tdsData.length === 0)

        return {
            tdsData,
            isLast
        }
    },
    template: `
        <div class="table">
            <div class="table-header">
                <div class="table-cell">id</div>
                <div class="table-cell">입력시간</div>
                <div class="table-cell">TDS 수치 (mg/L)</div>
            </div>
            <div v-for="row in tdsData" :key="row.id" class="table-row">
                <div class="table-cell">{{row.id}}</div>
                <div class="table-cell">{{row.created}}</div>
                <div class="table-cell">{{row.value_tds}}</div>
            </div>
            <div v-if="isLast" class="table-row">
                <div class="table-cell"></div>
                <div class="table-cell">
                    더 이상 불러올
                </div>
                <div class="table-cell">
                    데이터가 없습니다.
                </div>
            </div>
        </div>
    `
}