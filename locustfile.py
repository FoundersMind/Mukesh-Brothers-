from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task
    def load_filtered_and_special_data(self):
        self.client.get("/filtered_and_special_data/")

    @task
    def load_filtered_subproducts_without_product(self):
        self.client.get("/filtered-subproducts/")

    @task
    def load_filtered_subproducts_with_product(self):
        self.client.get("/filtered-subproducts/1/")

    @task
    def load_checkout_view(self):
        self.client.get("/checkout_view/")

   

    @task
    def load_login(self):
        self.client.get("/Login/")

 

    @task
    def load_subproduct(self):
        self.client.get("/subproduct/1/")

    @task
    def add_to_cart(self):
        self.client.post("/add_to_cart/", {"product_id": 1, "quantity": 1})

    @task
    def add_to_cart_index(self):
        self.client.post("/add_to_cart_index/", {"product_id": 1, "quantity": 1})

    # @task
    # def add_to_bucket(self):
    #     self.client.post("/add_to_bucket/", {"bucket_id": 1})

    # @task
    # def select_bucket(self):
    #     self.client.post("/select_bucket/", {"bucket_id": 1})

    @task
    def load_cart_view(self):
        self.client.get("/Cart/unit/1/unit_price/")

    @task
    def load_main_cart(self):
        self.client.get("/main_cart/")

    @task
    def get_unit_price(self):
        self.client.get("/get_unit_price/")

    @task
    def load_cart_view_general(self):
        self.client.get("/Cart/")

    @task
    def logout(self):
        self.client.get("/logout/")

    @task
    def remove_from_cart(self):
        self.client.get("/remove_from_cart/1/")

    @task
    def update_cart_item_quantity(self):
        self.client.post("/update_cart_item_quantity/1/", {"quantity": 2})

    @task
    def update_cart_item_quantity_index(self):
        self.client.post("/update_cart_item_quantity_index/1/", {"quantity": 2})

   

    @task
    def check_quantity(self):
        self.client.post("/check_quantity/", {"product_id": 1, "quantity": 1})

    @task
    def load_cart_view_specific(self):
        self.client.get("/cart_view/")

    @task
    def apply_coupon(self):
        self.client.post("/apply_coupon/", {"coupon_code": "MYSAF"})

    @task
    def search_results(self):
        self.client.get("/search/?q=test")

    @task
    def sign_in_with_google(self):
        # Replace this with the actual steps required to perform a Google sign-in.
        self.client.get("/auth/google/login")
