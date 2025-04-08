from django.core.management.base import BaseCommand
from data_integration.scrapers.scrape_tecnoempleo import TecnoempleoScraper
from data_integration.scrapers.fetch_infojobs import InfojobsScraper

class Command(BaseCommand):
    help = 'Import jobs from multiple sources'

    def handle(self, *args, **options):
        self.stdout.write('Starting job import...')
        total_jobs = 0

        # Tecnoempleo
        try:
            self.stdout.write('Importing from Tecnoempleo...')
            tecnoempleo = TecnoempleoScraper()
            jobs = tecnoempleo.scrape_jobs(pages=3)
            total_jobs += len(jobs)
            self.stdout.write(self.style.SUCCESS(f'Tecnoempleo import completed: {len(jobs)} jobs imported'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing from Tecnoempleo: {e}'))

        # Infojobs
        try:
            self.stdout.write('Importing from Infojobs...')
            infojobs = InfojobsScraper()
            infojobs.scrape_jobs()
            self.stdout.write(self.style.SUCCESS('Infojobs import completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing from Infojobs: {e}'))

        # LinkedIn (optional)
        try:
            from data_integration.scrapers.fetch_linkedin import LinkedInJobsFetcher
            self.stdout.write('Importing from LinkedIn...')
            linkedin = LinkedInJobsFetcher()
            linkedin.fetch_jobs()
            self.stdout.write(self.style.SUCCESS('LinkedIn import completed'))
        except ImportError:
            self.stdout.write(self.style.WARNING('LinkedIn integration not available'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing from LinkedIn: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Job import process completed. Total jobs imported: {total_jobs}'))
