# wow_api_dlt/rate_limiter.py
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
                sys.stdout.write(f"\rTokens available: {self.tokens:.2f}/{self.capacity} (Rate: {self.refill_rate_per_second} req/s)    ")
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
            sys.stdout.write(f"\rTokens available: {self.tokens:.2f}/{self.capacity} (Rate: {self.refill_rate_per_second} req/s)    ")
            sys.stdout.flush()


# Initialize a global/shared rate limiter instance
# Target: 36,000 requests/hour = 600 requests/minute = 10 requests/second
# Let's set a capacity that allows for some burst, e.g., 600 requests (1 minute's worth)
API_CAPACITY = 550
API_REFILL_RATE_PER_SECOND = 8 

blizzard_api_rate_limiter = TokenBucket(capacity=API_CAPACITY, refill_rate_per_second=API_REFILL_RATE_PER_SECOND)