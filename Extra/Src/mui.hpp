
#ifndef mui_hpp
#define mui_hpp

#include <string>

#include <lx_stddialog.hpp>
#include <lx_io.hpp>


namespace modo {
	namespace ui {

		class Monitor
		{
		public:
			Monitor(int ticksCount, std::string &title);

			void tick(float tickAmount);
			void setProgress(int tickAmount);
			void release();

		private:
			void _setup(int ticksCount, const std::string &title);

			CLxUser_StdDialogService _dialogService;
			CLxUser_Monitor _monitor;
			int _totalTicks;
			int _intTicksProgress;
			float _floatTicksProgress;
		};

	} // end ui namespace
} // end modo namespace

#endif
