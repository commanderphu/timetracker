-- =============================================================================
-- TimeTracker SQL Schema
--
-- Dieses Skript erstellt alle notwendigen Tabellen, Beziehungen und Ansichten
-- für die TimeTracker-Anwendung.
-- Führen Sie dieses Skript in Ihrem Supabase SQL-Editor aus.
-- =============================================================================


-- =============================================================================
-- 1. Tabelle für Benutzer (users)
-- =============================================================================
-- Speichert die Benutzerinformationen. Jeder Zeiteintrag muss einem
-- dieser Benutzer zugeordnet sein.

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

COMMENT ON TABLE public.users IS 'Speichert die Benutzerkonten.';


-- =============================================================================
-- 2. Tabelle für Zeiteinträge (time_entries)
-- =============================================================================
-- Speichert die einzelnen Zeitmessungen. Die Spalte `id` ist jetzt auch eine
-- UUID, um konsistent zu bleiben. Die `user_id` verweist auf die `users`-Tabelle.

CREATE TABLE IF NOT EXISTS public.time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,

    -- Fremdschlüssel-Beziehung: Stellt sicher, dass jeder Zeiteintrag
    -- einem existierenden Benutzer gehört.
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES public.users(id)
        ON DELETE CASCADE -- Optional: Löscht alle Zeiteinträge, wenn der Benutzer gelöscht wird.
);

COMMENT ON TABLE public.time_entries IS 'Speichert die Start- und Endzeiten der Zeiterfassung.';


-- =============================================================================
-- 3. Ansicht für die Zusammenfassung (v_time_summary)
-- =============================================================================
-- Eine Hilfsansicht, die die Arbeitszeit pro Tag und Benutzer zusammenfasst.
-- (Wird in der aktuellen App-Version nicht verwendet, aber nützlich für die Zukunft).

CREATE OR REPLACE VIEW public.v_time_summary AS
SELECT
    user_id,
    CAST(start_time AS DATE) AS day,
    SUM(end_time - start_time) AS total_duration
FROM
    public.time_entries
WHERE
    end_time IS NOT NULL
GROUP BY
    user_id,
    CAST(start_time AS DATE);

COMMENT ON VIEW public.v_time_summary IS 'Aggregiert die tägliche Arbeitszeit pro Benutzer.';


-- =============================================================================
-- 4. Beispieldaten einfügen
-- =============================================================================
-- Fügt Ihren persönlichen Benutzer hinzu, damit die Anwendung nach der
-- Einrichtung sofort funktioniert. Ersetzen Sie die Werte nach Bedarf.

INSERT INTO public.users (id, name, email)
VALUES ('b29ea098-08dc-4a63-bbd0-15ea5cdf9590', 'Joshua Phu Bein', 'deine@email.com')
ON CONFLICT (id) DO NOTHING; -- Verhindert Fehler, falls der Benutzer bereits existiert


-- =============================================================================
-- Skript Ende
-- =============================================================================
