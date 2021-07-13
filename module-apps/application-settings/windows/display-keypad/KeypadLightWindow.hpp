// Copyright (c) 2017-2020, Mudita Sp. z.o.o. All rights reserved.
// For licensing, see https://github.com/mudita/MuditaOS/LICENSE.md

#pragma once

#include <application-settings/windows/BaseSettingsWindow.hpp>
#include <application-settings/ApplicationSettings.hpp>

namespace gui
{
    class KeypadLightWindow : public BaseSettingsWindow
    {
      public:
        KeypadLightWindow(app::Application *app, app::settingsInterface::KeypdBacklightSettings *settings);

      private:
        void onBeforeShow(ShowMode mode, SwitchData *data) override;

        app::settingsInterface::KeypdBacklightSettings *keypadLightSettings;
        void switchHandler(bool &onOffSwitch);
        std::list<Option> buildOptionsList() override;

        unsigned int selectedOptionIndex = 0;
        bool isAlwaysOnSwitchOn          = false;
        bool isActiveSwitchOn            = false;
        bool isOffSwitchOn               = false;
    };
} // namespace gui