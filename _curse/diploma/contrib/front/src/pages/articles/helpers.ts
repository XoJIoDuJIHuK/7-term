import { fetch_data } from "../../helpers";
import { Config } from "../../settings";

export async function get_article(article_id: string) {
    const response = await fetch_data(`${Config.backend_address}/articles/${article_id}/`);
    return response ? response.data.article : undefined;
}