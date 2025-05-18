---

# 🍽️ Restaurant Recommendation System

This project is a scalable, cloud-native restaurant recommendation system designed to provide personalized dining suggestions to users. It leverages modern Python development, infrastructure-as-code with Terraform, and cloud-native deployment on AWS.

---

## 📁 Project Structure

* `api/`: Contains the backend API code responsible for serving restaurant recommendations.
* `scripts/`: Includes data processing and utility scripts.
* `terraform/`: Infrastructure-as-Code (IaC) configurations for deploying the system on cloud platforms.
* `tests/`: Contains different testing related code.

---

## 📦 Dependencies

### 🐍 Python & Libraries

Ensure you have **Python 3.8+** installed. You can install the required Python libraries using the `requirements.txt` file:

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Python Libraries Used:

* `boto3` – AWS SDK for Python, used for DynamoDB access and other AWS integrations.

### 🌍 Cloud & Infrastructure

* **Terraform** (>= 1.3.x): Used for infrastructure provisioning. Install it from [terraform.io](https://developer.hashicorp.com/terraform/downloads).
* **AWS Account**: You must have an active AWS account with the necessary IAM permissions to provision resources (e.g., DynamoDB, API Gateway, Lambda, etc.).

---

## ✅ Running the tests

1. **Install tests dependncies:**

   ```bash
   pip install -r requirements-tests.txt
   ```

2. **Run the python logic unit tests:**

   ```bash
   cd tests
   RESTAURANT_TABLE=fake_table pytest test_lambda_handler.py
   ```

---


---

## 🌐 Deployment with Terraform

1. **Initialize Terraform:**

   ```bash
   cd terraform
   terraform init
   ```

2. **Plan and Apply Infrastructure:**

   ```bash
   terraform plan
   terraform apply
   ```

   This will provision AWS resources like DynamoDB, Lambda functions, and API Gateway (as defined in your Terraform files).

   When the `terraform apply` command exits successfuly, you will see the `api_url` where you can reach the running service.
   ```bash
   Outputs:

   api_url = "https://1234abcd.execute-api.eu-north-1.amazonaws.com"
   ```

   Use it by calling `curl https://<my api url>/recommend?sentence="my search sentence"` .

   For example: 
   ```bash
   $ curl https://1234abcd.execute-api.eu-north-1.amazonaws.com/recommend?sentence="An italian place"`
   ```

---

## 🛠️ Planned Improvements

* ☁  **Additional cloud providers support**: GCP, Azure
* 🔍 **Improved Recommendation Logic**: Integrate ML models for smarter, more personalized suggestions.
* 🎨 **Web Frontend**: Add a simple web interface for users to interact with the API.
* ✅ **Unit & Integration Testing**: Improve test coverage and ensure production readiness.
* 🔁 **CI/CD Pipelines**: Automate deployment using GitHub Actions.
* 📊 **Analytics Integration**: Track usage data and recommendation performance metrics.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo, open issues, or submit pull requests with improvements, features, or bug fixes.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
