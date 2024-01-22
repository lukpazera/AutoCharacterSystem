#include "mui.hpp"

namespace modo {
	namespace ui {

		Monitor::Monitor(int ticksCount, std::string &title) :
			_totalTicks{ ticksCount },
			_intTicksProgress{ 0 },
			_floatTicksProgress{ 0.0f }
		{
			_setup(ticksCount, title);
		}

		void Monitor::_setup(int ticksCount, const std::string &title)
		{
			if (ticksCount < 1) { ticksCount = 1; }

			_dialogService.MonitorAllocate(title, _monitor);
			_monitor.Init(ticksCount);
		}

		void Monitor::tick(float tickAmount)
		{
			_floatTicksProgress += tickAmount;
			_intTicksProgress += int(tickAmount);

			int missingTicks = int(_floatTicksProgress) - _intTicksProgress;
			if (missingTicks > 0) {
				tickAmount += missingTicks;
				_intTicksProgress += missingTicks;
			}

			_monitor.Step(int(tickAmount));
		}

		void Monitor::setProgress(int tickAmount)
		{
			if (tickAmount <= int(_floatTicksProgress)) {
				return;
			}
			int missingTicks = tickAmount - _intTicksProgress;
			if (missingTicks > 0) {
				_monitor.Step(missingTicks);
			}

		}

		void Monitor::release()
		{
			_dialogService.MonitorRelease();
		}
	
	} // end ui namespace
} // end modo namespace
