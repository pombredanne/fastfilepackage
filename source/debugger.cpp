/*********************** Licensing *******************************************************
*
*   Copyright 2019 @ Evandro Coan, https://github.com/evandrocoan
*
*  This program is free software; you can redistribute it and/or modify it
*  under the terms of the GNU Lesser General Public License as published by the
*  Free Software Foundation; either version 2.1 of the License, or ( at
*  your option ) any later version.
*
*  This program is distributed in the hope that it will be useful, but
*  WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
*  Lesser General Public License for more details.
*
*  You should have received a copy of the GNU Lesser General Public License
*  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
*****************************************************************************************
*/


#include "debugger.h"

// [TUT] How to use an efficient debug system, which does not overload the final code -> C/C++ Language Implementation
// https://forums.alliedmods.net/showthread.php?t=277682#Cpp
//
// How do I use extern to share variables between source files?
// https://stackoverflow.com/questions/1433204/how-do-i-use-extern-to-share-variables-between-source-files
#if FASTFILE_DEBUG > DEBUG_LEVEL_DISABLED_DEBUG
  // initialize time tracking `extern` variables shared across all source files, do not change them
  std::clock_t _debugger_current_saved_c_time = std::clock();
  std::chrono::time_point<std::chrono::high_resolution_clock> _debugger_current_saved_chrono_time = std::chrono::high_resolution_clock::now();
#endif

