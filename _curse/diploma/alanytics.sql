DO $$
DECLARE
    article_record RECORD;
    random_reason_id INTEGER;
    status_value reportstatus;
BEGIN
    FOR article_record IN SELECT id FROM gptranslate_articles WHERE original_article_id IS NOT NULL LOOP
        SELECT id INTO random_reason_id
        FROM gptranslate_report_reasons
        ORDER BY random()
        LIMIT 1;

        SELECT myletter into status_value FROM ( SELECT unnest(enum_range(NULL::reportstatus)) as myletter ) sub ORDER BY random() LIMIT 1;

        INSERT INTO gptranslate_reports (id, text, article_id, status, reason_id, created_at)
        VALUES (
            gen_random_uuid(),
            substr(md5(random()::text), 1, 10),
            article_record.id,
            status_value,
            random_reason_id,
            now()
        );
    END LOOP;
END $$;

DO $$
BEGIN
    FOR i in 1..20 LOOP
        insert into gptranslate_articles VALUES (
            gen_random_uuid(),
            substr(md5(random()::text), 1, 10),
            substr(md5(random()::text), 1, 100),
            '195e9801-632f-470d-b1b6-51aa0eeb9419',
            1,
            'c10394b8-5cdd-4d88-9d25-0e654678ab64',
            null,
            now()
        );
    END LOOP;
END $$

DO $$
DECLARE
    article_record RECORD;
    status_value translationtaskstatus;
    model_id INTEGER;
    prompt_id INTEGER;
    target_language_id INTEGER;
BEGIN
    FOR article_record IN SELECT id FROM gptranslate_articles WHERE original_article_id IS NOT NULL LOOP
        select floor(random() * 2) + 1 into model_id;
        select floor(random() * 2) + 1 into prompt_id;
        select floor(random() * 5) + 1 into target_language_id;

        insert into gptranslate_translation_tasks (
            id, article_id, translated_article_id, target_language_id,
            model_id, prompt_id, status, created_at)
            values(
                gen_random_uuid(),
                'c10394b8-5cdd-4d88-9d25-0e654678ab64',
                article_record.id,
                target_language_id,
                model_id,
                prompt_id,
                'completed',
                now()
            );
    END LOOP;
END $$;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

select r.id as report_id, r.reason_id, t.model_id, t.prompt_id, r.status
from
    gptranslate_reports as r
    JOIN gptranslate_articles as a on a.id = r.article_id
    join gptranslate_translation_tasks as t on t.translated_article_id = a.id
where r.status = 'satisfied';
