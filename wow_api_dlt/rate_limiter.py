import time
import threading
import sys

class TokenBucket:
    def __init__(self, capacity, refill_rate_per_second):
        if capacity <= 0 or refill_rate_per_second <= 0:
            raise ValueError("Capacity and refill rate must be positive.")

        self.capacity = capacity
        self.refill_rate_per_second = refill_rate_per_second
        self.tokens = capacity  # Start with a full bucket
        self.last_refill_time = time.time()
        self.lock = threading.Lock() # Essential for thread safety

    def _refill_tokens(self):
        now = time.time()
        time_elapsed = now - self.last_refill_time
        refill_amount = time_elapsed * self.refill_rate_per_second
        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill_time = now

    def wait_for_token(self, num_tokens=1):
        if num_tokens <= 0:
            return

        with self.lock:
            self._refill_tokens()
            
            # Check if there are enough tokens AFTER refill
            if self.tokens >= num_tokens:
                self.tokens -= num_tokens
                # Print calls left in bucket
                # Using sys.stdout.write for in-place update in console applications
                sys.stdout.write(f"\rTokens available: {self.tokens:.2f}/{self.capacity} (Rate: {self.refill_rate_per_second} req/s)     ")
                sys.stdout.flush()
                return
            
            # If not enough tokens, calculate how long to wait
            tokens_needed = num_tokens - self.tokens
            time_to_wait = tokens_needed / self.refill_rate_per_second
            
            # Print the waiting message (on a new line to avoid overwriting progress bars)
            sys.stdout.write(f"\nRate limit hit! Waiting for {time_to_wait:.2f} seconds to acquire {num_tokens} token(s). Current tokens: {self.tokens:.2f}/{self.capacity}\n")
            sys.stdout.flush()

            # Reset last refill time *before* sleeping to accurately account for sleep duration
            self.last_refill_time = time.time() 
            time.sleep(time_to_wait)
            
            # After waiting, refill again and attempt to acquire tokens
            self._refill_tokens()
            self.tokens -= num_tokens # This should now succeed or indicate a logic error
            
            # Print calls left after waiting and acquiring
            sys.stdout.write(f"\rTokens available: {self.tokens:.2f}/{self.capacity} (Rate: {self.refill_rate_per_second} req/s)     ")
            sys.stdout.flush()


# --- New logic for the hourly break ---

class HourlyBreakRateLimiter:
    def __init__(self, token_bucket: TokenBucket, break_duration_minutes: int = 10, break_interval_hours: int = 1):
        if not isinstance(token_bucket, TokenBucket):
            raise TypeError("token_bucket must be an instance of TokenBucket.")
        if not isinstance(break_duration_minutes, (int, float)) or break_duration_minutes <= 0:
            raise ValueError("break_duration_minutes must be a positive number.")
        if not isinstance(break_interval_hours, (int, float)) or break_interval_hours <= 0:
            raise ValueError("break_interval_hours must be a positive number.")

        self.token_bucket = token_bucket
        self.break_duration_seconds = break_duration_minutes * 60
        self.break_interval_seconds = break_interval_hours * 3600 # 1 hour = 3600 seconds
        self.last_break_time = time.time() # Initialize to now
        self.break_lock = threading.Lock() # To prevent multiple threads from initiating a break

    def _check_and_apply_break(self):
        now = time.time()
        time_since_last_break = now - self.last_break_time

        if time_since_last_break >= self.break_interval_seconds:
            with self.break_lock:
                # Double-check inside the lock, as another thread might have just taken the break
                if now - self.last_break_time >= self.break_interval_seconds:
                    sys.stdout.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] Hourly break initiated! Pausing for {self.break_duration_seconds / 60:.0f} minutes.\n")
                    sys.stdout.flush()
                    time.sleep(self.break_duration_seconds)
                    self.last_break_time = time.time() # Update last break time after the break
                    sys.stdout.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] Hourly break finished. Resuming operations.\n")
                    sys.stdout.flush()

    def wait_for_token_with_break(self, num_tokens=1):
        self._check_and_apply_break() # Check for and apply break before waiting for token
        self.token_bucket.wait_for_token(num_tokens)


# Initialize a global/shared rate limiter instance (original configuration)
# Target: 36,000 requests/hour = 600 requests/minute = 10 requests/second
# Let's set a capacity that allows for some burst, e.g., 600 requests (1 minute's worth)
API_CAPACITY = 550
API_REFILL_RATE_PER_SECOND = 8 

# IMPORTANT: These global instances are now directly used by client.py
# So, they are defined here for consistency and clarity.
_blizzard_token_bucket_instance = TokenBucket(capacity=API_CAPACITY, refill_rate_per_second=API_REFILL_RATE_PER_SECOND)
blizzard_api_rate_limiter = HourlyBreakRateLimiter(
    _blizzard_token_bucket_instance, 
    break_duration_minutes=10, 
    break_interval_hours=1
)

# Example usage (for testing this file directly, if needed)
if __name__ == "__main__":
    print("Testing rate_limiter.py directly with hourly break...")
    # This test simulates calls and demonstrates the hourly break
    # It will take over an hour to see the break if break_interval_hours is 1.
    # For quick testing, you can adjust break_interval_hours to a smaller value (e.g., 1/60 for 1 minute).
    
    # Let's make it easy to test the break immediately by setting interval to 1 minute
    test_limiter = HourlyBreakRateLimiter(
        TokenBucket(capacity=10, refill_rate_per_second=1), # Small bucket for quick hits
        break_duration_minutes=0.1, # 6 seconds break for testing
        break_interval_hours=1/60 # Every 1 minute for testing
    )

    start_time = time.time()
    for i in range(200): # Simulate many API calls
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] Attempting API call {i+1}...")
        test_limiter.wait_for_token_with_break()
        # Simulate some work or actual API call here
        time.sleep(0.5) # Simulate time between calls, adjust as needed

        if i % 20 == 0:
            sys.stdout.write("\n") # Newline every 20 calls for readability

    print(f"\nSimulated API calls finished after {time.time() - start_time:.2f} seconds.")