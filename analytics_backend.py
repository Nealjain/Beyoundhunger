#!/usr/bin/env python3
"""
Backend Analytics Module for Beyond Hunger
Tracks user logins, deliveries, and pending requests
"""

import sqlite3
import logging
from datetime import datetime, timedelta
import os
import csv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='analytics.log'
)
logger = logging.getLogger(__name__)

class AnalyticsBackend:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
        self._init_analytics_tables()

    def _get_connection(self):
        """Create and return a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def _init_analytics_tables(self):
        """Initialize analytics tables if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create tables for analytics
            cursor.executescript("""
                -- Table for tracking user logins
                CREATE TABLE IF NOT EXISTS analytics_user_login (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES auth_user(id)
                );

                -- Table for tracking site visits
                CREATE TABLE IF NOT EXISTS analytics_site_visit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_url TEXT NOT NULL,
                    visit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES auth_user(id)
                );

                -- Table for tracking delivery status changes
                CREATE TABLE IF NOT EXISTS analytics_delivery_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donation_id INTEGER NOT NULL,
                    old_status TEXT,
                    new_status TEXT NOT NULL,
                    change_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(donation_id) REFERENCES food_donation_fooddonation(id)
                );
            """)

            conn.commit()
            logger.info("Analytics tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing analytics tables: {str(e)}")
            raise
        finally:
            conn.close()

    def track_user_login(self, user_id):
        """Track when a user logs in"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analytics_user_login (user_id)
                VALUES (?)
            """, (user_id,))
            
            conn.commit()
            logger.debug(f"Tracked login for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking user login: {str(e)}")
            raise
        finally:
            conn.close()

    def track_site_visit(self, page_url, user_id=None):
        """Track site visits with optional user identification"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analytics_site_visit (page_url, user_id)
                VALUES (?, ?)
            """, (page_url, user_id))
            
            conn.commit()
            logger.debug(f"Tracked visit to {page_url} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking site visit: {str(e)}")
            raise
        finally:
            conn.close()

    def track_delivery_status_change(self, donation_id, old_status, new_status):
        """Track changes in delivery status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analytics_delivery_status 
                (donation_id, old_status, new_status)
                VALUES (?, ?, ?)
            """, (donation_id, old_status, new_status))
            
            conn.commit()
            logger.debug(f"Tracked status change for donation {donation_id}: {old_status} -> {new_status}")
            
        except Exception as e:
            logger.error(f"Error tracking delivery status change: {str(e)}")
            raise
        finally:
            conn.close()

    def get_login_statistics(self, days=30):
        """Get login statistics for the specified number of days"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    DATE(login_time) as login_date,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) as total_logins
                FROM analytics_user_login
                WHERE DATE(login_time) >= ?
                GROUP BY DATE(login_time)
                ORDER BY login_date DESC
            """, (start_date,))
            
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting login statistics: {str(e)}")
            raise
        finally:
            conn.close()

    def get_delivery_statistics(self):
        """Get statistics about deliveries and requests"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get delivery statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_donations,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_donations,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_donations
                FROM food_donation_fooddonation
            """)
            
            donation_stats = cursor.fetchone()
            
            # Get request statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_requests,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_requests
                FROM food_donation_physicaldonationrequest
            """)
            
            request_stats = cursor.fetchone()
            
            return {
                'donations': dict(donation_stats),
                'requests': dict(request_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting delivery statistics: {str(e)}")
            raise
        finally:
            conn.close()

    def get_popular_pages(self, days=7):
        """Get most visited pages in the last specified days"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    page_url,
                    COUNT(*) as visit_count,
                    COUNT(DISTINCT user_id) as unique_visitors
                FROM analytics_site_visit
                WHERE DATE(visit_time) >= ?
                GROUP BY page_url
                ORDER BY visit_count DESC
                LIMIT 10
            """, (start_date,))
            
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Error getting popular pages: {str(e)}")
            raise
        finally:
            conn.close()

    def get_user_activity_summary(self, user_id):
        """Get summary of a user's activity"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user's donations
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_donations,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as completed_donations
                FROM food_donation_fooddonation
                WHERE donor_id IN (SELECT id FROM food_donation_donor WHERE email = (
                    SELECT email FROM auth_user WHERE id = ?
                ))
            """, (user_id,))
            
            donation_stats = cursor.fetchone()
            
            # Get user's requests
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_requests
                FROM food_donation_physicaldonationrequest
                WHERE requester_id = ?
            """, (user_id,))
            
            request_stats = cursor.fetchone()
            
            # Get user's login count
            cursor.execute("""
                SELECT COUNT(*) as login_count
                FROM analytics_user_login
                WHERE user_id = ?
            """, (user_id,))
            
            login_stats = cursor.fetchone()
            
            return {
                'donations': dict(donation_stats),
                'requests': dict(request_stats),
                'logins': dict(login_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity summary: {str(e)}")
            raise
        finally:
            conn.close()

    def export_login_statistics_csv(self, start_date, end_date, output_file):
        """Export login statistics to CSV for a date range"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(login_time) as login_date,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) as total_logins
                FROM analytics_user_login
                WHERE DATE(login_time) BETWEEN ? AND ?
                GROUP BY DATE(login_time)
                ORDER BY login_date
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Unique Users', 'Total Logins'])
                for row in rows:
                    writer.writerow([row['login_date'], row['unique_users'], row['total_logins']])
            
            logger.debug(f"Login statistics exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting login statistics: {str(e)}")
            raise
        finally:
            conn.close()

    def export_delivery_statistics_csv(self, start_date, end_date, output_file):
        """Export delivery statistics to CSV for a date range"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(change_time) as change_date,
                    COUNT(*) as total_changes,
                    SUM(CASE WHEN new_status = 'pending' THEN 1 ELSE 0 END) as new_pending,
                    SUM(CASE WHEN new_status = 'delivered' THEN 1 ELSE 0 END) as new_delivered
                FROM analytics_delivery_status
                WHERE DATE(change_time) BETWEEN ? AND ?
                GROUP BY DATE(change_time)
                ORDER BY change_date
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Total Changes', 'New Pending', 'New Delivered'])
                for row in rows:
                    writer.writerow([
                        row['change_date'],
                        row['total_changes'],
                        row['new_pending'],
                        row['new_delivered']
                    ])
            
            logger.debug(f"Delivery statistics exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting delivery statistics: {str(e)}")
            raise
        finally:
            conn.close()

    def export_page_visits_csv(self, start_date, end_date, output_file):
        """Export page visit statistics to CSV for a date range"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    page_url,
                    DATE(visit_time) as visit_date,
                    COUNT(*) as visit_count,
                    COUNT(DISTINCT user_id) as unique_visitors
                FROM analytics_site_visit
                WHERE DATE(visit_time) BETWEEN ? AND ?
                GROUP BY page_url, DATE(visit_time)
                ORDER BY visit_date, visit_count DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Page URL', 'Total Visits', 'Unique Visitors'])
                for row in rows:
                    writer.writerow([
                        row['visit_date'],
                        row['page_url'],
                        row['visit_count'],
                        row['unique_visitors']
                    ])
            
            logger.debug(f"Page visit statistics exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting page visit statistics: {str(e)}")
            raise
        finally:
            conn.close()

    def get_reports_directory(self):
        """Get or create the reports directory"""
        reports_dir = os.path.join(os.path.dirname(self.db_path), 'analytics_reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        return reports_dir 