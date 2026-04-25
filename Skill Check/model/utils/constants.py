SECTION_HEADERS = {
    "contact":        r"(contact|phone|linkedin|github|address|معلومات الاتصال|تواصل)",
    "summary":        r"(summary|profile|objective|about\s*me|personal\s*statement|نبذة|الهدف|ملخص)",
    "education":      r"(education|academic|university|degree|school|college|التعليم|المؤهلات|الدراسة|المؤهل)",
    "experience":     r"(experience|employment|work\s*history|internship|career|الخبرة|الخبرات|العمل|سجل العمل)",
    "skills":         r"(skills|technologies|tools|competencies|المهارات|تقنيات|أدوات)",
    "projects":       r"(projects|portfolio|work\s*samples|المشاريع|مشاريع|أعمال)",
    "certifications": r"(certif|license|credential|course|training|شهادات|دورات|تدريب)",
    "awards":         r"(award|honor|achievement|scholarship|جوائز|تكريم|إنجازات)",
    "languages":      r"(language|spoken|fluency|اللغات|لغات)",
    "references":     r"(reference|recommendation|مراجع|توصيات)",
}


CRITICAL_SECTIONS = ["summary", "education", "experience", "skills"]

MISSING_SECTION_MESSAGES_EN = {
    "summary":        "Add a Profile Summary (2-3 sentences about yourself and your goals).",
    "education":      "Add an Education section with your degree, university, and graduation year.",
    "experience":     "Add a Work Experience or Internship section.",
    "skills":         "Add a Skills section listing your technical and soft skills.",
    "projects":       "Add a Projects section — even academic or personal projects count.",
    "certifications": "Add any Certifications or online courses you have completed.",
    "contact":        "Make sure your contact info (email, LinkedIn) is clearly listed.",
}

MISSING_SECTION_MESSAGES_AR = {
    "summary":        "أضف 'نبذة مهنية' (2-3 جمل توضح مهاراتك وأهدافك).",
    "education":      "أضف قسم 'التعليم' مع ذكر التخصص، الجامعة، وسنة التخرج.",
    "experience":     "أضف قسم 'الخبرة العملية' أو التدريب المهني.",
    "skills":         "أضف قسم 'المهارات' لذكر الأدوات والتقنيات التي تتقنها.",
    "projects":       "أضف قسم 'المشاريع' — المشاريع الأكاديمية والشخصية مهمة جداً.",
    "certifications": "أضف أي 'شهادات' أو دورات تدريبية حصلت عليها.",
    "contact":        "تأكد من إضافة معلومات التواصل الخاصة بك (الإيميل، حساب لينكد إن).",
}

ACTION_VERBS = [
    "developed", "built", "led", "managed", "designed",
    "implemented", "created", "improved", "analyzed", "achieved",
]
