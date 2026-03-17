-- Randevu Sistemi - Supabase SQL Kurulumu
-- Bu SQL kodu Supabase Dashboard > SQL Editor'a yapıştırılmalıdır

-- appointments tablosu oluştur
CREATE TABLE IF NOT EXISTS public.appointments (
    id BIGSERIAL PRIMARY KEY,
    queue_number INTEGER NOT NULL,
    note TEXT DEFAULT '',
    status VARCHAR(50) DEFAULT 'Beklemede' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- RLS (Row Level Security) etkinleştir - Güvenlik için
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;

-- Tüm kullanıcılar için okuma/yazma politikası (geliştirme aşamasında)
CREATE POLICY "Allow all" ON public.appointments
    FOR ALL
    TO public
    USING (true)
    WITH CHECK (true);

-- Otomatik updated_at güncelleme fonksiyonu
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger oluştur
DROP TRIGGER IF EXISTS update_appointments_updated_at ON public.appointments;
CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON public.appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Realtime (canlı güncelleme) etkinleştir
ALTER PUBLICATION supabase_realtime ADD TABLE public.appointments;

-- Index'ler (performans için)
CREATE INDEX IF NOT EXISTS idx_appointments_status ON public.appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_created_at ON public.appointments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_appointments_queue_number ON public.appointments(queue_number);

-- Örnek veri ekle (opsiyonel - test için)
-- INSERT INTO public.appointments (queue_number, note, status) 
-- VALUES (1, 'Test randevu', 'Beklemede');
