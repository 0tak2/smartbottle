import { computed } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

export default {
    props: [
        'value_volumeDiffer', 'value_tds',
        'created_hydrationData', 'created_tdsData'
    ],
    setup(props) {
        const {
            value_volumeDiffer, created_hydrationData,
            value_tds, created_tdsData
        } = props
        
        const hydrationSign = computed(() => {
            return parseInt(value_volumeDiffer) < 0 ? '+' : ''
        })

        const hydrationElapsedTime = computed(() => {
            const prevTime = new Date(created_hydrationData)
            const currentTime = new Date()
            const difference = Math.abs(prevTime.getTime() - currentTime.getTime())
            const differenceByHours = difference / (1000 * 60 * 60)
            
            let approxi = null
            let dimension = null
            let warning = null

            if (differenceByHours < 1) {
                approxi = Math.round(difference / (1000 * 60))
                dimension = '분'
                warning = 'warning-0' // 1시간 미만인 경우 warning-0
            } else {
                approxi = Math.round(differenceByHours)
                dimension = '시간'

                if (differenceByHours > 3) {
                    warning = 'warning-2'  // 3시간 초과인 경우 warning-2
                } else {
                    warning = 'warning-1'  // 3시간 이하 1시간 초과인 경우 warning-1
                }
            }

            return {
                elapsedTime: approxi,
                dimension: dimension,
                warning: warning
            };
        })

        const tdsWarning = computed(() => {
            if (value_tds < 30) {
                return 'warning-0' // 30 미만인 경우 warning-0
            } else if (value_tds < 60) {
                return 'warning-1' // 30 이상 60 미만인 경우 warning-1
            } else {
                return 'warning-2' // 60 이상인 경우 warning-2
            }
        })

        return {
            hydrationSign,
            hydrationElapsedTime,
            tdsWarning,
            value_volumeDiffer,
            value_tds,
            created_hydrationData,
            created_tdsData
        }
    },
    template: `
        <div class="home-card full-width">
            <div class="home-card-panel" v-bind:class="hydrationElapsedTime.warning">
                <div class="panel-title">수분 섭취</div>
                <div class="panel-value">{{hydrationSign}}{{Math.abs(value_volumeDiffer)}}ml</div>
                <div>
                    {{created_hydrationData}} <br />
                    (약 {{hydrationElapsedTime.elapsedTime}}{{hydrationElapsedTime.dimension}} 경과)
                </div>
            </div>
            <div class="home-card-panel" v-bind:class="tdsWarning">
                <div class="panel-title">TDS</div>
                <div class="panel-value">{{value_tds}}mg/L</div>
                <div>{{created_tdsData}}</div>
            </div>
        </div>
    `
}