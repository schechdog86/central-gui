from PyQt6.QtCore import QObject, pyqtSignal


class WebScraperViewModel(QObject):
    job_created_signal = pyqtSignal(str)
    status_updated_signal = pyqtSignal(dict)
    overall_status_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, scraper_manager):
        super().__init__()
        self.scraper_manager = scraper_manager

    def create_job(self, url: str, options: dict):
        try:
            job_id = self.scraper_manager.create_scrape_job(url, options)
            self.job_created_signal.emit(job_id)
        except Exception as e:
            self.error_signal.emit(f"Error creating job: {str(e)}")

    def get_status(self, job_id: str = ""):
        try:
            status = self.scraper_manager.get_status(job_id)
            if job_id:  # Specific job status
                self.status_updated_signal.emit(status)
            else:  # Overall status
                self.overall_status_signal.emit(status)
        except Exception as e:
            self.error_signal.emit(f"Error getting status: {str(e)}")

    def get_results(self, job_id: str):
        # This might be integrated into get_status or be a separate display
        # For now, get_status will return results if job is completed.
        try:
            results = self.scraper_manager.get_results(job_id)
            if results:
                # Or a dedicated results_signal
                self.status_updated_signal.emit(results)
            else:
                self.status_updated_signal.emit({
                    "message": "No results found or job not completed.",
                    "job_id": job_id
                })
        except Exception as e:
            self.error_signal.emit(f"Error getting results: {str(e)}")
