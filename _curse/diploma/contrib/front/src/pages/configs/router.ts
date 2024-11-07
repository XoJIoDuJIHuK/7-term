import BaseLayout from "../../components/BaseLayout.vue"
import List from "./List.vue"
import Edit from "./Create.vue"

export default {
    path: '/configs/',
    component: BaseLayout,
    children: [
        { path: '', component: List },
        { path: 'create/', component: Edit },
    ]
}