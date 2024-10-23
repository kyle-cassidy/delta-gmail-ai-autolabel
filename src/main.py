from pipeline.step_1_email_retrieval import retrieve_emails
from pipeline.step_2_security_vetting import perform_security_vetting
from pipeline.step_3_content_processing import process_content
from pipeline.step_4_classification import classify_content
from pipeline.step_5_data_integration import integrate_data

def main():
    emails = retrieve_emails()
    vetted_emails = perform_security_vetting(emails)
    processed_content = process_content(vetted_emails)
    classified_data = classify_content(processed_content)
    integrate_data(classified_data)

if __name__ == "__main__":
    main()
