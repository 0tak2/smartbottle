import { computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

export default {
    props: [
        'hydrationData'
    ],
    setup(props) {
        const { hydrationData } = props
        
        function signHelper(value) {
            if (parseInt(value) > 0) {
                return '+'
            } else {
                return ''
            }
        }

        function intakeHelper(differ) {
            if (differ < 0) {
                return String(differ * -1)
            } else {
                return '해당없음'
            }
        }

        const isLast = computed(() => hydrationData.length === 0)

        return {
            signHelper,
            intakeHelper,
            hydrationData,
            isLast
        }
    },
    template: `
        <div class="table">
            <div class="table-header">
                <div class="table-cell">id</div>
                <div class="table-cell">입력시간</div>
                <div class="table-cell">현재 부피 (ml)</div>
                <div class="table-cell">부피 변화 (ml)</div>
                <div class="table-cell">섭취량 추정 (ml)</div>
            </div>
            <div v-for="row in hydrationData" :key="row.id" class="table-row">
                <div class="table-cell">{{row.id}}</div>
                <div class="table-cell">{{row.created}}</div>
                <div class="table-cell">{{row.value_volume}}</div>
                <div class="table-cell">{{signHelper(row.value_differ)}}{{row.value_differ}}</div>
                <div class="table-cell">{{intakeHelper(row.value_differ)}}</div>
            </div>
            <div v-if="isLast" class="table-row">
                <div class="table-cell"></div>
                <div class="table-cell">
                    더 이상 불러올
                </div>
                <div class="table-cell">
                    데이터가 없습니다.
                </div>
                <div class="table-cell"></div>
                <div class="table-cell"></div>
            </div>
        </div>
    `
}