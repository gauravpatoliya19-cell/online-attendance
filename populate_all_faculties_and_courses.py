import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from attendance_app.models import Department, Course

FACULTIES_AND_COURSES = [
    {
        "code": "FoS",
        "name": "Faculty of Science",
        "courses": [
            {"degree": "MCA", "name": "Master of Computer Applications"},
            {"degree": "BCA", "name": "Bachelor of Computer Applications"},
            {"degree": "B.Sc IT", "name": "Information Technology"},
            {"degree": "M.Sc IT", "name": "Information Technology"},
            {"degree": "M.Sc Data Science", "name": "Data Science & Big Data"},
            {"degree": "M.Sc Cyber Security", "name": "Cyber Security & Digital Forensics"},
            {"degree": "PGDCA", "name": "Post Graduate Diploma in Computer Applications"},
            {"degree": "B.Sc Biotech", "name": "Biotechnology"},
            {"degree": "M.Sc Biotech", "name": "Biotechnology"},
            {"degree": "B.Sc Micro", "name": "Microbiology"},
            {"degree": "M.Sc Micro", "name": "Microbiology"},
            {"degree": "B.Sc Biochem", "name": "Biochemistry"},
            {"degree": "M.Sc Biochem", "name": "Biochemistry"},
            {"degree": "B.Sc Chemistry", "name": "Chemistry"},
            {"degree": "M.Sc Chemistry", "name": "Organic / Analytical Chemistry"},
            {"degree": "M.Sc Ind. Chem", "name": "Industrial Chemistry"},
            {"degree": "B.Sc Physics", "name": "Physics"},
            {"degree": "M.Sc Physics", "name": "Physics"},
            {"degree": "B.Sc Maths", "name": "Mathematics"},
            {"degree": "M.Sc Maths", "name": "Mathematics"},
            {"degree": "B.Sc Statistics", "name": "Statistics & Applied Analytics"},
            {"degree": "BMLT", "name": "Medical Laboratory Technology"},
            {"degree": "PGDMLT", "name": "Post Graduate Diploma in Medical Lab Technology"},
        ]
    },
    {
        "code": "FoET",
        "name": "Faculty of Engineering & Technology",
        "courses": [
            {"degree": "B.Tech CE", "name": "Computer Engineering"},
            {"degree": "B.Tech AI & ML", "name": "Artificial Intelligence & Machine Learning"},
            {"degree": "B.Tech IT", "name": "Information Technology"},
            {"degree": "B.Tech Mech", "name": "Mechanical Engineering"},
            {"degree": "B.Tech Civil", "name": "Civil Engineering"},
            {"degree": "B.Tech Electrical", "name": "Electrical Engineering"},
            {"degree": "B.Tech EC", "name": "Electronics & Communication"},
            {"degree": "M.Tech SE", "name": "Software Engineering"},
            {"degree": "M.Tech AI & DS", "name": "AI & Data Science"},
            {"degree": "M.Tech PE", "name": "Production Engineering"},
            {"degree": "M.Tech TE", "name": "Transportation Engineering"},
            {"degree": "M.Tech Structure", "name": "Structural Engineering"},
            {"degree": "M.Tech Power", "name": "Power Electronics & Drives"},
            {"degree": "Diploma CE", "name": "Diploma in Computer Engineering"},
            {"degree": "Diploma IT", "name": "Diploma in Information Technology"},
            {"degree": "Diploma Mech", "name": "Diploma in Mechanical Engineering"},
            {"degree": "Diploma Civil", "name": "Diploma in Civil Engineering"},
            {"degree": "Diploma Electrical", "name": "Diploma in Electrical Engineering"},
        ]
    },
    {
        "code": "FoM",
        "name": "Faculty of Business, Management & Commerce",
        "courses": [
            {"degree": "BBA", "name": "Bachelor of Business Administration"},
            {"degree": "BBA (Hons)", "name": "BBA Honours in Global Business"},
            {"degree": "BBA (BFSI)", "name": "Banking, Financial Services & Insurance"},
            {"degree": "BBA (Digital Mkt)", "name": "Digital Marketing & E-Commerce"},
            {"degree": "MBA", "name": "Master of Business Administration (General)"},
            {"degree": "MBA (Finance)", "name": "MBA in Financial Management"},
            {"degree": "MBA (Marketing)", "name": "MBA in Marketing Management"},
            {"degree": "MBA (HRM)", "name": "MBA in Human Resource Management"},
            {"degree": "MBA (Analytics)", "name": "MBA in Business Analytics"},
            {"degree": "Executive MBA", "name": "Executive Master of Business Administration"},
            {"degree": "B.Com", "name": "Bachelor of Commerce"},
            {"degree": "B.Com (Hons)", "name": "B.Com Honours in Accounting & Finance"},
            {"degree": "B.Com (Banking)", "name": "B.Com in Banking & Insurance"},
            {"degree": "M.Com", "name": "Master of Commerce"},
        ]
    },
    {
        "code": "FoP",
        "name": "Faculty of Pharmacy",
        "courses": [
            {"degree": "B.Pharm", "name": "Bachelor of Pharmacy"},
            {"degree": "M.Pharm (Pharmaceutics)", "name": "M.Pharm in Pharmaceutics"},
            {"degree": "M.Pharm (QA)", "name": "M.Pharm in Pharmaceutical Quality Assurance"},
            {"degree": "M.Pharm (Pharmacology)", "name": "M.Pharm in Pharmacology"},
            {"degree": "M.Pharm (Chemistry)", "name": "M.Pharm in Pharmaceutical Chemistry"},
            {"degree": "Pharm.D", "name": "Doctor of Pharmacy"},
            {"degree": "Ph.D Pharmacy", "name": "Doctor of Philosophy in Pharmaceutical Sciences"},
        ]
    },
    {
        "code": "FoA",
        "name": "Faculty of Arts & Humanities",
        "courses": [
            {"degree": "B.A. English", "name": "English Literature & Linguistics"},
            {"degree": "M.A. English", "name": "English Literature & Literary Theory"},
            {"degree": "B.A. Psychology", "name": "Clinical & Applied Psychology"},
            {"degree": "M.A. Psychology", "name": "Psychology & Behavioral Studies"},
            {"degree": "B.A. Economics", "name": "Economics & Public Policy"},
            {"degree": "M.A. Economics", "name": "Economics & Econometrics"},
            {"degree": "B.A. Sociology", "name": "Sociology & Social Welfare"},
            {"degree": "BJMC", "name": "Journalism & Mass Communication"},
            {"degree": "MJMC", "name": "Master of Journalism & Mass Communication"},
            {"degree": "B.Lib.I.Sc", "name": "Bachelor of Library & Information Science"},
            {"degree": "M.Lib.I.Sc", "name": "Master of Library & Information Science"},
        ]
    }
]

def populate():
    print("Populating all official University Faculties and Comprehensive Courses...")
    total_courses = 0
    
    for fac in FACULTIES_AND_COURSES:
        dept_obj, _ = Department.objects.update_or_create(
            code=fac["code"],
            defaults={"name": fac["name"]}
        )
        print(f"\n[Faculty] {dept_obj.code} - {dept_obj.name}")
        
        for c in fac["courses"]:
            course_obj, created = Course.objects.update_or_create(
                department=dept_obj,
                degree=c["degree"],
                defaults={"name": c["name"]}
            )
            total_courses += 1
            status = "Created" if created else "Updated"
            print(f"   -> [{status}] {course_obj.degree}: {course_obj.name}")

    print(f"\nSUCCESS: Successfully populated {len(FACULTIES_AND_COURSES)} Faculties and {total_courses} official courses!")

if __name__ == "__main__":
    populate()
