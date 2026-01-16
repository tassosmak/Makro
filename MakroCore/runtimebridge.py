# # Makro/MakroCore/KernelBridge.py
# from Makro.MakroCore.runtime import KernelRuntime

# # This variable will hold our single, persistent runtime instance
# _kernel_instance = None

# def get_kernel(user=None):
#     """
#     Returns the shared kernel instance.
#     If it doesn't exist yet, create it (optionally with a user context).
#     """
#     global _kernel_instance
#     if _kernel_instance is None:
#         _kernel_instance = KernelRuntime(user)
#     return _kernel_instance

# Makro/MakroCore/RuntimeBridge.py
from Makro.MakroCore.Runtime import KernelRuntime

# Hold the shared runtime instance
_kernel_instance = None
def fallback_get_kernel():
    """
    Fallback to get the kernel without user context.
    Used internally when no user is logged in yet.
    """
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = KernelRuntime("default")
    return _kernel_instance

def get_kernel(user=None, force_reload=False):
    """
    Return the shared KernelRuntime instance.
    - If it doesn't exist, it will be created.
    - If force_reload=True, the kernel will be re-initialized for the new user.
    """
    global _kernel_instance

    # Reload if forced or not initialized yet
    if _kernel_instance is None or force_reload:
        if user is None:
            # raise RuntimeError(
            #     "Kernel initialization requires a username when force_reload=True or on first load."
            # )
            return fallback_get_kernel()
        _kernel_instance = KernelRuntime(user)

    # Guard against calls before login
    if _kernel_instance is None and user is None:
    #     raise RuntimeError(
    #         "Kernel not initialized yet — call get_kernel(<user>) after login."
    #     )
        return fallback_get_kernel()
    

    return _kernel_instance


def reset_kernel():
    """
    Completely reset the kernel (clears the shared instance).
    Next get_kernel(<user>) call will rebuild it.
    """
    global _kernel_instance
    _kernel_instance = None

