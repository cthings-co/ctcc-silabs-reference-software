# Contributing to CTCC Silicon Labs Reference Software

Thank you for your interest in contributing to this project.

## Development Environment

Follow the instructions in [README.md](README.md) to set up
the Zephyr development environment and build the firmware.

The project uses a pinned Zephyr workspace defined in `west.yml`.

## Making Changes

1. Create a separate branch for your changes.
2. Follow the existing coding conventions.
3. Keep changes focused and well documented.
4. Verify that the firmware builds successfully.
5. Run the available tests before submitting a pull request.

## Testing

Run the Python unit tests:

    python3 -m unittest discover -s tests -p 'test_*.py' -v

Firmware changes should also be verified for the supported
MGM240P board variants.

See README.md for detailed build instructions.

## Developer Certificate of Origin (DCO)

All contributions must include a DCO sign-off.

Configure Git with your real name and email address:

    git config user.name "Your Name"
    git config user.email "your.email@example.com"

CTHINGS.CO employees should use their official company email.

Sign off each commit using:

    git commit -s -m "Describe your changes"

The sign-off must match the commit author's identity.

This adds a Signed-off-by line to the commit message.

The sign-off certifies that you have the right to submit
the contribution under the project's license.

## Pull Requests

Before submitting a pull request:

- Ensure all commits include a DCO sign-off.
- Run the relevant tests.
- Verify the firmware builds successfully.
- Describe the changes and their purpose.
- Include relevant testing information.

Pull requests are subject to review and automated CI checks.

## Licensing

This project is licensed under Apache License 2.0.

New source files should include appropriate copyright notices
and SPDX license identifiers.

Preserve existing third-party copyright and license notices.

Do not commit credentials, private keys, or sensitive data.
