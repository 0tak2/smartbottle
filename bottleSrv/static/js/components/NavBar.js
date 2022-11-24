export default {
    props: [
        'features'
    ],
    setup(props, { emit }) {
        const { features } = props
        function handleSelection(feature) {
            emit('selected', feature)
        }
        
        return {
            handleSelection,
            features
        }
    },
    emits: ['selected'],
    template: `
        <div class="nav">
            <div class="nav-title">스마트보틀</div>
            <div class="nav-items">
                <div class="nav-item" v-on:click="() => handleSelection(features.HOME)">홈 &nbsp&nbsp | </div>
                <div class="nav-item" v-on:click="() => handleSelection(features.HYDR)">&nbsp&nbsp 하이드레이션 &nbsp&nbsp | </div>
                <div class="nav-item" v-on:click="() => handleSelection(features.TDS)">&nbsp&nbsp TDS 수치</div>
            </div>
        </div>
    `
  }