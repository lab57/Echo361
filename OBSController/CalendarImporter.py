from icalendar import Calendar
from datetime import datetime, timedelta
from pymongo import MongoClient
import recurring_ical_events
import pytz


class CalendarImporter:
    def __init__(self, mongo_uri, database_name, collection_name):
        """Initialize with MongoDB connection details"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def import_from_ical(self, ical_path, future_days=30):
        """Import events from an ICS file"""
        try:
            with open(ical_path, "rb") as f:
                calendar = Calendar.from_ical(f.read())

            # Calculate date range for recurring events
            start_date = datetime.now(pytz.UTC)
            end_date = start_date + timedelta(days=future_days)

            # Get all events including recurring ones
            events = recurring_ical_events.of(calendar).between(start_date, end_date)

            count = 0
            for event in events:
                # Extract event details
                mongo_event = {
                    "title": str(event.get("summary", "No Title")),
                    "description": str(event.get("description", "")),
                    "start_time": event.get("dtstart").dt,
                    "end_time": event.get("dtend").dt,
                    "location": str(event.get("location", "")),
                    "ical_uid": str(event.get("uid", "")),
                    "source": "ical",
                }

                # Handle all-day events
                if isinstance(mongo_event["start_time"], datetime):
                    mongo_event["all_day"] = False
                else:
                    mongo_event["all_day"] = True
                    # Convert date to datetime for MongoDB
                    mongo_event["start_time"] = datetime.combine(
                        mongo_event["start_time"], datetime.min.time()
                    )
                    mongo_event["end_time"] = datetime.combine(
                        mongo_event["end_time"], datetime.min.time()
                    )

                # Insert or update in MongoDB
                self.collection.update_one(
                    {"ical_uid": mongo_event["ical_uid"]},
                    {"$set": mongo_event},
                    upsert=True,
                )
                count += 1

            return count

        except Exception as e:
            print(f"Error importing from iCal: {str(e)}")
            raise

    def __del__(self):
        """Close MongoDB connection"""
        self.client.close()


# Example usage
if __name__ == "__main__":
    importer = CalendarImporter(
        mongo_uri="your_mongodb_atlas_uri",
        database_name="scheduling",
        collection_name="meetings",
    )

    # Import from Google Calendar
    # First, download credentials.json from Google Cloud Console
    num_google_events = importer.import_from_google_calendar(
        credentials_path="path/to/credentials.json"
    )
    print(f"Imported {num_google_events} events from Google Calendar")

    # Import from ICS file
    num_ical_events = importer.import_from_ical(ical_path="path/to/calendar.ics")
    print(f"Imported {num_ical_events} events from ICS file")
