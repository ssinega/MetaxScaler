# Contributing to Support Ticket OpenEnv

Thank you for your interest in improving the Support Ticket triage environment!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/support-ticket-env.git
   cd support-ticket-env
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Copy `.env.example` to `.env` and fill in your API keys.

## Workflow

### Running Tests
Always run the test suite before submitting changes:
```bash
pytest tests/test_env_quality.py -v
```

### Adding New Tickets
To add more realistic support queries:
1. Open `env/dataset.py`.
2. Add a new dictionary entry to the `TICKETS` list.
3. Ensure it has `id`, `query`, `category`, `priority`, `action`, and `tags`.

### Adding New Tasks
To define new RL challenges:
1. Open `env/tasks.py`.
2. Add a new `Task` instance to the `TASKS` dictionary.
3. Define the `reward_weights` and `scored_fields`.

## Contribution Checklist

- [ ] Code follows existing style and Pydantic models.
- [ ] New features include corresponding unit tests.
- [ ] `validate_submission.py` passes locally.
- [ ] `README.md` is updated if interface changes.
- [ ] No API keys are committed to the repository.
