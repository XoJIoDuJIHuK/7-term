import BaseLayout from "../../components/BaseLayout.vue"
import Create from "./Create.vue"
import Get from "./Get.vue"

export default {
    path: '/articles/:article_id/report/',
    component: BaseLayout,
    children: [
        { path: '', component: Get },
        { path: 'create', component: Create },
    ]
}