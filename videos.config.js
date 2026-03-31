/**
 * Список роликов YouTube по категориям.
 * Меняйте id и title здесь — index.html подхватит через window.MP_VIDEO_CONFIG
 *
 * ID берутся из URL: https://www.youtube.com/watch?v=VIDEO_ID
 *
 * Если ролик открывается на youtube.com, но не грузится в приложении —
 * у автора может быть отключено «Воспроизведение на других сайтах» (встраивание).
 * Замените id на другой ролик или добавьте запасной в конец списка категории.
 *
 * ─── Как искать ролики для esports (киберспорт / комп. игры) ─────────────────
 * Каналы и запросы (официальные хайлайты чаще разрешают embed):
 *   • "PGL CS2 major highlights", "BLAST Premier CS2 highlights"
 *   • "LoL Esports highlights", "Worlds highlights day 1"
 *   • "Rocket League Esports RLCS highlights", "RLCS major highlights"
 *   • "VALORANT Champions Tour highlights", "VCT highlights"
 * На странице ролика: «Поделиться» → «Встроить» — если встраивание недоступно,
 * приложение перейдёт к следующему id в списке категории.
 */
window.MP_VIDEO_CONFIG = {
    /**
     * NHL — официальные хайлайты матчей (названия по роликам на YouTube).
     */
    hockey: [
        { id: "Pt7fmczwAOk", title: "🏒 Монреаль — Каролина | NHL Highlights, 29.03.2026" },
        { id: "Xp0Z9ROuiS8", title: "🏒 Бостон — Коламбус | NHL Highlights, 29.03.2026" },
        { id: "2YYgGehIuPo", title: "🏒 Монреаль — Каролина | альт. монтаж NHL" },
        { id: "hzLRpvXetrg", title: "🏒 Чикаго — Нью-Джерси | NHL Highlights, 29.03.2026" },
        { id: "HMTwAu3Sy84", title: "🏒 Нэшвилл — Тампа-Бэй | NHL Highlights, 29.03.2026" },
    ],
    /**
     * Футбол — реальные ролики (ESPN FC, FIFA World Cup, товарищеские).
     */
    football: [
        { id: "ApjQmxuW5jA", title: "⚽ Франция — Бразилия | Full Game, ESPN FC" },
        { id: "ZpvJ2OoCvlY", title: "⚽ Саудовская Аравия — Аргентина | ЧМ-2022" },
        { id: "DP4epIVQOCk", title: "⚽ ЧМ-2022: голы, 2-й тур (30+ мин)" },
        { id: "BmioYKIGzTg", title: "⚽ Нидерланды — Аргентина | серия пенальти ЧМ-2022" },
        { id: "J1RDiaSUEdY", title: "⚽ США — Бельгия | товарищеский, 28.03.2026" },
    ],
    /** Соревновательные игры: шутеры, MOBA, спорт-симы на кибер-арене */
    esports: [
        { id: "WYZyveDwft4", title: "🎮 CS2 — NAVI vs G2 (PGL Major)" },
        { id: "9CfbbZbCV7I", title: "🎮 CS2 — G2 vs Liquid (BLAST)" },
        { id: "HG8Feb-sRa8", title: "🎮 CS2 — G2 vs Vitality (BLAST)" },
        { id: "w0-uua72aig", title: "🎮 LoL — хайлайты Knockout (Worlds)" },
        { id: "Yxd_EMy6fa4", title: "🎮 LoL — G2 vs TES (Worlds)" },
    ],
};
