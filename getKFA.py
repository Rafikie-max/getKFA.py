# Install Kaspersky Free Antivirus for Windows
# This script requests for free antivirus installer from free-antivirus download page API and install it with a fake activation code.
# https://www.kaspersky.com/downloads/free-antivirus
import os
import subprocess
import tempfile

import requests

ALLOWED_LOCALES = ["en-INT", "zh-Hans-CN"]

# The FAKE_ACTIVATION_CODE skips the Kaspersky account login process when first run KFA.
# The code is hardcoded in the Kaspersky activation dll file and used only for free versions.
# We are only sure about codes for the two locales now.
FAKE_ACTIVATION_CODE = {
    "en-INT": "ZM4YW-FUTDY-W9B62-GSK26",
    "zh-Hans-CN": "3SXCM-M9RJM-6985N-PWKP7",
}

SITES = {
    "en-INT": "https://www.kaspersky.com",
    "zh-Hans-CN": "https://www.kaspersky.com.cn",
}


def get_installer_url(locale):
    site = SITES[locale]
    params = {
        "productcodes": "5003617",
        "businesspurposes": "Update",
        "licensetiers": "Free",
        "sites": [site],
    }
    response = requests.get(
        "https://api-router.kaspersky-labs.com/downloads/search/v3/b2c",
        params=params,
    )
    response.raise_for_status()
    versions = response.json()[0]["response"]["Windows"]["Kaspersky4Win"]["Downloader"][
        site
    ]
    max_version_key = max(versions, key=lambda k: float(k) if k.isdigit() else -1) # Get the max version, usually only one version, just in case
    url = versions[str(max_version_key)][locale]["Link"]
    return url


def download_and_get_path(url):
    temp_dir = tempfile.gettempdir()
    response = requests.get(url, stream=True)
    response.raise_for_status()
    file_name = url.split("/")[-1]
    with open(os.path.join(temp_dir, file_name), "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return os.path.join(temp_dir, file_name)


if __name__ == "__main__":
    if os.name != "nt":
        raise NotImplementedError("Only Windows is supported")

    default_locale = "zh-Hans-CN"

    if len(os.sys.argv) > 1:
        locale = os.sys.argv[1]
        if locale not in ALLOWED_LOCALES:
            raise ValueError(f"Unsupported locale: {locale}")
    else:
        locale = default_locale

    if locale not in FAKE_ACTIVATION_CODE:
        raise ValueError(f"Unsupported locale: {locale}")

    print("This script will install Kaspersky Free Antivirus for Windows")
    print("Attention: If you cancel the installation, do not use the installer shortcut on the desktop, it may not activate KFA automatically.")
    installer_url = get_installer_url(locale)
    print(installer_url)
    installer_path = download_and_get_path(installer_url)
    print(installer_path)

    subprocess.Popen(
        [installer_path, "/pACTIVATIONCODE=" + FAKE_ACTIVATION_CODE[locale]],
    )