#!/usr/bin/env python3
"""Generate the fictional demo programme shipped with Conference Compass.

Everything produced here is synthetic: the congress, sessions, rooms and
"Speaker A"-style faculty names do not describe any real event or person.
Replace public/program.json with your own data in the same schema to use the
planner for a real meeting (see docs/PROGRAM-SCHEMA.md).

Usage: python3 scripts/make-demo-program.py > public/program.json
"""
import json
import sys
from string import ascii_uppercase

CONFERENCE = {
    "id": "demo-em-2027",
    "shortName": "COMPASS",
    "yearTag": "’27",
    "name": {"tr": "Demo Acil Tıp Kongresi 2027", "en": "Demo Emergency Medicine Congress 2027"},
    "dates": {"tr": "6–9 Nisan 2027", "en": "6–9 April 2027"},
    "venue": {"tr": "Örnek Kongre Merkezi", "en": "Example Congress Centre"},
    "timezone": "Europe/Istanbul",
    "utcOffset": "+03:00",
    "timezoneLabel": {"tr": "Türkiye saati (UTC+3)", "en": "Türkiye time (UTC+3)"},
    "url": None,
    "notice": {
        "tr": "Bu program tamamen kurgusaldır; gerçek bir kongreyi veya kişiyi temsil etmez.",
        "en": "This programme is entirely fictional and does not represent any real congress or person.",
    },
}
DAYS = ["2027-04-06", "2027-04-07", "2027-04-08", "2027-04-09"]
ROOMS = {str(100 + i): f"Hall {c}" for i, c in enumerate("ABCDEF")}
ROOM_ID = {v: k for k, v in ROOMS.items()}

# (tr title, en title, [(tr talk, en talk), ...])
SESSIONS = [
    ("Acil Serviste Yapay Zekâ: Abartı mı Gerçek mi?", "AI in the Emergency Department: Hype or Reality?",
     [("Triyajda makine öğrenmesi", "Machine learning at triage"), ("Klinik karar destek sistemlerinde hata kaynakları", "Failure modes of clinical decision support"), ("Büyük dil modelleri ve klinik dokümantasyon", "Large language models and clinical documentation")]),
    ("Sepsiste İlk Saat", "The First Hour in Sepsis",
     [("Erken tanı skorları", "Early recognition scores"), ("Sıvı mı, erken vazopresör mü?", "Fluids or early vasopressors?"), ("Laktat rehberli resüsitasyon", "Lactate-guided resuscitation")]),
    ("Şokta Yatak Başı Ultrasonografi", "Point-of-Care Ultrasound in Shock",
     [("RUSH protokolü", "The RUSH protocol"), ("VExUS ile venöz konjesyon", "Venous congestion with VExUS"), ("Sıvı yanıtlılığını öngörmek", "Predicting fluid responsiveness")]),
    ("Zor Havayolu: Planlı Yaklaşım", "The Difficult Airway: A Planned Approach",
     [("Fizyolojik zor havayolu", "The physiologically difficult airway"), ("Videolaringoskopi ilk tercih mi?", "Is video laryngoscopy first-line?"), ("Cerrahi havayoluna geçiş kararı", "Deciding on a surgical airway")]),
    ("Çoklu Travmada Kanama Kontrolü", "Haemorrhage Control in Major Trauma",
     [("Masif transfüzyon protokolü", "Massive transfusion protocol"), ("REBOA nerede durur?", "Where does REBOA stand?"), ("Traneksamik asit güncellemesi", "Tranexamic acid update")]),
    ("Kardiyak Arrestte Yeni Kanıtlar", "New Evidence in Cardiac Arrest",
     [("Mekanik KPR cihazları", "Mechanical CPR devices"), ("E-CPR için hasta seçimi", "Patient selection for E-CPR"), ("Arrest sonrası bakım paketi", "Post-arrest care bundle")]),
    ("Akut İnmede Zaman Kazanmak", "Saving Time in Acute Stroke",
     [("Büyük damar oklüzyonu tanıma", "Recognising large vessel occlusion"), ("Trombolizde güncel pencere", "Current thrombolysis windows"), ("Hastane öncesi bildirim", "Prehospital notification")]),
    ("Toksikolojide Zor Vakalar", "Challenging Cases in Toxicology",
     [("Yeni sentetik opioidler", "Novel synthetic opioids"), ("Kalsiyum kanal bloker zehirlenmesi", "Calcium channel blocker poisoning"), ("Antidot stok yönetimi", "Antidote stock management")]),
    ("Çocuk Acilde Kırmızı Bayraklar", "Red Flags in Paediatric Emergencies",
     [("Ateşli bebeğe yaklaşım", "The febrile infant"), ("Pediatrik sepsiste sıvı", "Fluids in paediatric sepsis"), ("Çocuk istismarını tanımak", "Recognising child maltreatment")]),
    ("Afet Tıbbında Hazırlık", "Preparedness in Disaster Medicine",
     [("Kitlesel yaralanmada triyaj", "Triage in mass casualty incidents"), ("Hastane afet planı tatbikatı", "Hospital disaster drills"), ("Deprem sonrası ezilme sendromu", "Crush syndrome after earthquakes")]),
    ("Araştırma Yöntemleri: Kanıtı Okumak", "Research Methods: Reading the Evidence",
     [("Gözlemsel çalışmalarda yanlılık", "Bias in observational studies"), ("Tanısal doğruluk çalışmaları", "Diagnostic accuracy studies"), ("Meta-analizi eleştirel okumak", "Appraising a meta-analysis")]),
    ("Acil Tıp Eğitiminde Simülasyon", "Simulation in Emergency Medicine Education",
     [("Senaryo tasarımı", "Scenario design"), ("Etkili debriefing", "Effective debriefing"), ("Yerinde simülasyon", "In-situ simulation")]),
    ("Hasta Güvenliği ve Tıbbi Hata", "Patient Safety and Medical Error",
     [("Atlanan tanılar", "Missed diagnoses"), ("İletişim kopukluğu ve devir", "Communication breakdown at handover"), ("Hata sonrası açıklama", "Disclosure after error")]),
    ("Yaşlı Hastada Acil Bakım", "Emergency Care of the Older Adult",
     [("Deliryum taraması", "Delirium screening"), ("Düşme sonrası değerlendirme", "Assessment after a fall"), ("Polifarmasi riskleri", "Risks of polypharmacy")]),
    ("Elektrolit Acilleri", "Electrolyte Emergencies",
     [("Ağır hiponatremi", "Severe hyponatraemia"), ("Hiperkalemide EKG", "ECG in hyperkalaemia"), ("Diyabetik ketoasidoz protokolleri", "Diabetic ketoacidosis protocols")]),
    ("Mekanik Ventilasyonun Temelleri", "Mechanical Ventilation Essentials",
     [("Akciğer koruyucu ventilasyon", "Lung-protective ventilation"), ("Acilde yüksek akış oksijen", "High-flow oxygen in the ED"), ("Non-invaziv ventilasyonda başarısızlık", "Non-invasive ventilation failure")]),
    ("Klinik Yapay Zekâyı Değerlendirmek", "Evaluating Clinical AI Tools",
     [("Dış doğrulama neden şart?", "Why external validation matters"), ("Model kayması ve izleme", "Model drift and monitoring"), ("Etik ve sorumluluk", "Ethics and accountability")]),
    ("Göğüs Ağrısında Hızlı Karar", "Rapid Decisions in Chest Pain",
     [("Yüksek duyarlıklı troponin algoritmaları", "High-sensitivity troponin pathways"), ("OMI kavramı", "The occlusion MI paradigm"), ("Aort diseksiyonunu atlamamak", "Not missing aortic dissection")]),
    ("Baş Ağrısı ve Baş Dönmesi", "Headache and Dizziness",
     [("Subaraknoid kanamayı dışlamak", "Ruling out subarachnoid haemorrhage"), ("HINTS muayenesi", "The HINTS examination"), ("Migren tedavisinde yenilikler", "Advances in migraine treatment")]),
    ("Hastane Öncesi Acil Bakım", "Prehospital Emergency Care",
     [("Sahada havayolu", "Airway in the field"), ("Hastane öncesi kan ürünleri", "Prehospital blood products"), ("Uzaktan tıbbi yönlendirme", "Remote medical direction")]),
    ("Acil Serviste Liderlik", "Leadership in the Emergency Department",
     [("Kalabalık yönetimi", "Managing crowding"), ("Ekip içi geri bildirim", "Feedback within the team"), ("Tükenmişlikle mücadele", "Tackling burnout")]),
    ("Dijital Sağlık ve Teletıp", "Digital Health and Telemedicine",
     [("Tele-triyaj", "Tele-triage"), ("Giyilebilir sensörler", "Wearable sensors"), ("Veri güvenliği", "Data security")]),
    ("Pulmoner Emboli: Tanıdan Tedaviye", "Pulmonary Embolism: From Diagnosis to Treatment",
     [("Klinik karar kuralları", "Clinical decision rules"), ("Yüksek riskli emboli", "High-risk embolism"), ("Ayaktan tedavi seçimi", "Selecting outpatient treatment")]),
    ("Gastrointestinal Kanama", "Gastrointestinal Bleeding",
     [("Risk skorları", "Risk scores"), ("Antikoagülan geri döndürme", "Anticoagulant reversal"), ("Endoskopi zamanlaması", "Timing of endoscopy")]),
    ("Yanık ve Elektrik Yaralanmaları", "Burns and Electrical Injuries",
     [("Sıvı formülleri", "Fluid formulas"), ("İnhalasyon hasarı", "Inhalation injury"), ("Elektrik yaralanmasında kardiyak izlem", "Cardiac monitoring after electrical injury")]),
    ("Anafilaksi ve Anjiyoödem", "Anaphylaxis and Angioedema",
     [("Adrenalinin zamanlaması", "Timing of adrenaline"), ("Bifazik reaksiyon", "Biphasic reactions"), ("Bradikinin aracılı anjiyoödem", "Bradykinin-mediated angioedema")]),
    ("Gebelikte Acil Durumlar", "Emergencies in Pregnancy",
     [("Ektopik gebelik", "Ectopic pregnancy"), ("Gebelikte travma", "Trauma in pregnancy"), ("Peripartum kardiyomiyopati", "Peripartum cardiomyopathy")]),
    ("Kanıta Dayalı Tıp Kulübü", "Evidence-Based Medicine Journal Club",
     [("Yılın en önemli çalışmaları", "Top papers of the year"), ("Negatif çalışmalardan ders", "Lessons from negative trials"), ("Kılavuzlar arasında çelişki", "When guidelines disagree")]),
    ("Acil Tıpta Etik İkilemler", "Ethical Dilemmas in Emergency Medicine",
     [("Karar verme kapasitesi", "Decision-making capacity"), ("Resüsitasyon kararları", "Resuscitation decisions"), ("Kaynak kısıtlılığında adalet", "Fairness under resource constraints")]),
    ("Acil Serviste Ağrı Yönetimi", "Pain Management in the Emergency Department",
     [("Ketamin ile analjezi", "Analgesia with ketamine"), ("Bölgesel bloklar", "Regional nerve blocks"), ("Opioid koruyucu yaklaşım", "Opioid-sparing strategies")]),
    ("Çevresel Aciller", "Environmental Emergencies",
     [("Hipotermi", "Hypothermia"), ("Sıcak çarpması", "Heat stroke"), ("Boğulmaya yakın durumlar", "Drowning")]),
    ("Kritik Hastanın Transferi", "Transferring the Critically Ill Patient",
     [("Transfer öncesi kontrol listesi", "Pre-transfer checklist"), ("Yoğun bakım yatağı beklerken", "While waiting for an ICU bed"), ("Transfer sırasında monitörizasyon", "Monitoring during transfer")]),
    ("Acil Tıpta Veri Bilimi", "Data Science in Emergency Medicine",
     [("Açık veri setleri", "Open datasets"), ("Tekrarlanabilir analiz", "Reproducible analysis"), ("Sentetik veri ile eğitim", "Teaching with synthetic data")]),
    ("Aritmilere Pratik Yaklaşım", "A Practical Approach to Arrhythmias",
     [("Geniş QRS taşikardi", "Wide-complex tachycardia"), ("Atriyal fibrilasyonda hız mı ritim mi?", "Rate or rhythm in atrial fibrillation"), ("Bradikardide pacing", "Pacing for bradycardia")]),
    ("Nöbet ve Status Epileptikus", "Seizures and Status Epilepticus",
     [("İkinci basamak antiepileptikler", "Second-line antiseizure drugs"), ("Konvülzif olmayan status", "Non-convulsive status"), ("Çocukta status epileptikus", "Status epilepticus in children")]),
    ("Göğüs Travması", "Chest Trauma",
     [("Tansiyon pnömotoraks", "Tension pneumothorax"), ("Kaburga kırıklarında analjezi", "Analgesia for rib fractures"), ("Resüsitatif torakotomi", "Resuscitative thoracotomy")]),
    ("Acil Tıpta Yazmak ve Yayımlamak", "Writing and Publishing in Emergency Medicine",
     [("Hakem gözünden makale", "A manuscript through a reviewer's eyes"), ("Dergi seçimi", "Choosing a journal"), ("Yapay zekâ ve akademik yazım", "AI and academic writing")]),
    ("Sosyal Belirleyiciler ve Kırılgan Gruplar", "Social Determinants and Vulnerable Groups",
     [("Evsiz hastalar", "Patients experiencing homelessness"), ("Dil engeli", "Language barriers"), ("Sık başvuran hasta", "Frequent attenders")]),
    ("Acil Serviste Ultrason Rehberli İşlemler", "Ultrasound-Guided Procedures in the ED",
     [("Periferik damar yolu", "Peripheral vascular access"), ("Santral venöz kateter", "Central venous catheters"), ("Parasentez ve torasentez", "Paracentesis and thoracentesis")]),
    ("Karın Ağrısında Tuzaklar", "Pitfalls in Abdominal Pain",
     [("Mezenter iskemi", "Mesenteric ischaemia"), ("Yaşlıda apandisit", "Appendicitis in older adults"), ("Görüntüleme seçimi", "Choosing imaging")]),
    ("Karar Destek Araçlarının Geleceği", "The Future of Decision Support Tools",
     [("Açıklanabilir modeller", "Explainable models"), ("Klinik iş akışına entegrasyon", "Integration into clinical workflow"), ("Düzenleyici çerçeve", "Regulatory frameworks")]),
    ("Sepsiste Antibiyotik Seçimi", "Antibiotic Selection in Sepsis",
     [("Ampirik tedavi", "Empirical therapy"), ("Direnç örüntüleri", "Resistance patterns"), ("De-eskalasyon", "De-escalation")]),
]
ABSTRACTS = [
    ("Sözlü Bildiriler: Resüsitasyon", "Oral Abstracts: Resuscitation"),
    ("Sözlü Bildiriler: Travma", "Oral Abstracts: Trauma"),
    ("Sözlü Bildiriler: Yapay Zekâ ve Dijital Sağlık", "Oral Abstracts: AI and Digital Health"),
    ("Sözlü Bildiriler: Eğitim", "Oral Abstracts: Education"),
    ("Sözlü Bildiriler: Toksikoloji", "Oral Abstracts: Toxicology"),
    ("Sözlü Bildiriler: Pediatri", "Oral Abstracts: Paediatrics"),
]
COURSES = [
    ("Yatak Başı Ultrasonografi Kursu", "Point-of-Care Ultrasound Course"),
    ("İleri Havayolu Becerileri Kursu", "Advanced Airway Skills Course"),
    ("Mekanik Ventilatör Kursu", "Mechanical Ventilation Course"),
    ("Travma Resüsitasyonu Beceri Kursu", "Trauma Resuscitation Skills Course"),
]
SATELLITES = [
    ("Uydu Sempozyumu: Antikoagülasyonda Güncel Yaklaşımlar", "Satellite Symposium: Current Approaches to Anticoagulation"),
    ("Uydu Sempozyumu: Acilde Analjezi", "Satellite Symposium: Analgesia in the ED"),
    ("Uydu Sempozyumu: Dijital Triyaj Platformları", "Satellite Symposium: Digital Triage Platforms"),
    ("Uydu Sempozyumu: Sepsiste Biyobelirteçler", "Satellite Symposium: Biomarkers in Sepsis"),
    ("Uydu Sempozyumu: Taşınabilir Görüntüleme", "Satellite Symposium: Portable Imaging"),
]


def speaker_names(n):
    names = list(ascii_uppercase)
    names += [a + b for a in ascii_uppercase for b in ascii_uppercase]
    return [f"Speaker {x}" for x in names[:n]]


SPEAKERS = speaker_names(48)
DATE_LABEL = {
    "tr": lambda d: f"{int(d[8:])} Nisan {d[:4]}",
    "en": lambda d: f"{int(d[8:])} April {d[:4]}",
}

events, speaker_sessions = [], {}
next_id = 1001
sp_cursor = 0


def take_people(k):
    global sp_cursor
    out = []
    for _ in range(k):
        out.append(SPEAKERS[sp_cursor % len(SPEAKERS)])
        sp_cursor += 1
    return out


def add(date, start, end, room, etype, tr, en, talks=None, chairs=0, extra=0, desc=None):
    global next_id
    eid = str(next_id)
    next_id += 1
    talks = talks or []
    chair_names = take_people(chairs) if chairs else []
    talk_speakers = take_people(len(talks)) if talks else []
    others = take_people(extra) if extra else []
    people_names = list(dict.fromkeys(chair_names + talk_speakers + others))
    people = [{"id": f"p{SPEAKERS.index(n) + 1}", "name": n} for n in people_names]
    for n in people_names:
        speaker_sessions.setdefault(n, []).append(eid)
    tr_desc = (desc or {}).get("tr", "")
    en_desc = (desc or {}).get("en", "")
    translations = {}
    for lang, title in (("tr", tr), ("en", en)):
        chairs_label = ("Oturum Başkanları: " if lang == "tr" else "Chairs: ") + ", ".join(chair_names) if chair_names else ""
        t_list = [{"title": (t[0] if lang == "tr" else t[1]), "speaker": s} for t, s in zip(talks, talk_speakers)]
        description = tr_desc if lang == "tr" else en_desc
        detail = "\n".join(filter(None, [title, DATE_LABEL[lang](date), f"{start} - {end}", room, chairs_label, description] + [f"{x['title']} — {x['speaker']}" for x in t_list]))
        translations[lang] = {
            "listing": title, "title": title, "chairs": chairs_label, "description": description,
            "talks": t_list, "people": people, "sourceUrl": None, "detailText": detail,
        }
    events.append({"id": eid, "date": date, "start": start, "end": end, "room": room, "roomId": ROOM_ID.get(room, ""),
                   "type": etype, "valid": True, "translations": translations})
    return eid


def brk(date, start, end, tr, en, room="Hall A"):
    add(date, start, end, room, "break", tr, en)


# Day 1: pre-congress courses and opening
for i, (tr, en) in enumerate(COURSES):
    add(DAYS[0], "09:00", "16:30", ROOMS[str(102 + i)], "course", tr, en, extra=3,
        desc={"tr": "Uygulamalı kurs; ayrı kayıt gerektirir.", "en": "Hands-on course; separate registration required."})
brk(DAYS[0], "12:30", "13:30", "Öğle Arası", "Lunch Break", room="Hall A")
add(DAYS[0], "17:00", "18:00", "Hall A", "ceremony", "Açılış Töreni ve Açılış Konferansı", "Opening Ceremony and Keynote",
    talks=[("Acil tıbbın önümüzdeki on yılı", "The next decade of emergency medicine")], chairs=2)
add(DAYS[0], "18:15", "19:15", "Hall B", "satellite", *SATELLITES[0], talks=[("Sunum", "Presentation")])

SLOTS = [("08:30", "09:40"), ("09:50", "11:00"), ("11:30", "12:40"), ("14:00", "15:10"), ("15:30", "16:40")]
session_iter = iter(SESSIONS)
abstract_iter = iter(ABSTRACTS)
sat_iter = iter(SATELLITES[1:])
for day in DAYS[1:3]:
    for si, (start, end) in enumerate(SLOTS):
        for hall in "ABCD":
            room = f"Hall {hall}"
            if hall == "D" and si in (1, 3, 4) and day == DAYS[1] or hall == "D" and si in (1, 3, 4) and day == DAYS[2]:
                tr, en = next(abstract_iter, (None, None))
                if tr:
                    add(day, start, end, room, "abstract", tr, en, chairs=2, extra=4)
                    continue
            tr, en, talks = next(session_iter)
            add(day, start, end, room, "session", tr, en, talks=talks, chairs=2)
    brk(day, "11:00", "11:30", "Kahve Arası", "Coffee Break")
    brk(day, "12:40", "14:00", "Öğle Arası", "Lunch Break")
    for hall in "EF":
        tr, en = next(sat_iter)
        add(day, "12:50", "13:50", f"Hall {hall}", "satellite", tr, en, talks=[("Sunum", "Presentation")])

# Day 4: short morning and closing
for si, (start, end) in enumerate([("09:00", "10:10"), ("10:40", "11:50")]):
    for hall in "ABC":
        tr, en, talks = next(session_iter)
        add(DAYS[3], start, end, f"Hall {hall}", "session", tr, en, talks=talks, chairs=2)
brk(DAYS[3], "10:10", "10:40", "Kahve Arası", "Coffee Break")
add(DAYS[3], "12:00", "12:45", "Hall A", "ceremony", "Ödüller ve Kapanış", "Awards and Closing", chairs=2)

speakers = []
for name in SPEAKERS:
    ids = speaker_sessions.get(name, [])
    if not ids:
        continue
    by_id = {e["id"]: e for e in events}
    text = {}
    for lang in ("tr", "en"):
        lines = [name, "Konuşmalar" if lang == "tr" else "Talks"]
        for i in ids:
            e = by_id[i]
            lines += [DATE_LABEL[lang](e["date"]), e["room"], f"{e['start']} - {e['end']}", e["translations"][lang]["title"]]
        text[lang] = {"text": "\n".join(lines), "sourceUrl": None}
    speakers.append({"id": f"p{SPEAKERS.index(name) + 1}", "name": name, "sessionIds": ids, "translations": text})

counts = {d: sum(1 for e in events if e["date"] == d) for d in DAYS}
program = {
    "title": CONFERENCE["name"]["en"],
    "conference": CONFERENCE,
    "fetchedAt": "2027-01-15T09:00:00+00:00",
    "source": None,
    "days": DAYS,
    "rooms": ROOMS,
    "countsByDay": counts,
    "events": events,
    "speakers": speakers,
    "sourceIssues": [],
}
json.dump(program, sys.stdout, ensure_ascii=False, indent=1)
sys.stdout.write("\n")
