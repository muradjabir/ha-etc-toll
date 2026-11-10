# Expressway ETC Toll (Sri Lanka) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub release](https://img.shields.io/github/v/release/muradjabir/ha-etc-toll?style=for-the-badge)](https://github.com/muradjabir/ha-etc-toll/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Track your **Expressway Electronic Toll Collection (ETC)** prepaid card balance and status directly in Home Assistant.

This custom component queries the official [Expressway Sri Lanka (RDA) Quick Top-Up](https://www.exway.rda.gov.lk/etconline/en/quick-topup) portal in real time without requiring login credentials, passwords, or SMS OTPs.

---

## Features

- **Real-Time Prepaid Balance:** Monitor your current ETC account balance in `LKR` (`monetary` device class, `total` state class).
- **Card Status Monitoring:** Track whether the ETC card is active and accepted by the RDA system.
- **Dedicated Device per Card:** Each configured ETC card creates its own device in Home Assistant with balance and status sensors.
- **Low Balance Automation Ready:** Easily set up automations to receive push notifications when your ETC card balance falls below a threshold before driving on the highway.
- **100% Asynchronous & Lightweight:** Built using Home Assistant's native `aiohttp` client session with zero external python dependencies.
- **Config Flow & Options Flow:** Simple UI setup with options to customize polling frequency (default 4 hours, minimum 30 minutes).

---

## Installation

### Method 1: Via HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=muradjabir&repository=ha-etc-toll&category=integration)

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the **three dots** in the top-right corner and select **Custom repositories**.
3. Add the repository URL:
   ```text
   https://github.com/muradjabir/ha-etc-toll
   ```
4. Select Category: **Integration** and click **Add**.
5. Search for **ETC Toll (Sri Lanka)** and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the latest release or clone this repository.
2. Copy the `custom_components/etc_toll` directory into your Home Assistant `<config_dir>/custom_components/` folder.
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom-right corner.
3. Search for **ETC Toll (Sri Lanka)**.
4. Enter your **ETC Card Number** (e.g. `0065653` or 16-digit card number printed on your ETC card).
5. Click **Submit**. Home Assistant will immediately verify the card and create your device and sensors.

---

## Example Automation: Low ETC Balance Alert

Receive a push notification on your mobile phone whenever your ETC card balance drops below Rs. 1,000:

```yaml
alias: "ETC Low Balance Alert"
description: "Notify when Expressway ETC balance is low"
trigger:
  - platform: numeric_state
    entity_id: sensor.etc_card_0065653_balance
    below: 1000
condition: []
action:
  - action: notify.notify
    data:
      title: "Low ETC Highway Balance"
      message: >-
        Your Expressway ETC card balance is Rs. {{ states('sensor.etc_card_0065653_balance') }}.
        Please top up at https://www.exway.rda.gov.lk/etconline/en/quick-topup before entering the expressway.
mode: single
```

---

## Disclaimer

This integration is an independent open-source project and is not officially affiliated with, endorsed by, or sponsored by the Road Development Authority (RDA) of Sri Lanka.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

