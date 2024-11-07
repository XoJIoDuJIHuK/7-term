import BaseLayout from "../../components/BaseLayout.vue"
import OriginalList from "./OriginalList.vue"
import Get from "./Get.vue"
import Edit from "./Edit.vue"
import TranslationList from "./TranslationList.vue"

export default {
    path: '/articles/',
    component: BaseLayout,
    children: [
        { path: '', component: OriginalList },
        { path: ':original_article_id/translations/', component: TranslationList },
        { path: 'create/', component: Edit },
        { path: ':article_id/get/', component: Get, props: true },
        { path: ':article_id/update/', component: Edit, props: true },
    ]
}