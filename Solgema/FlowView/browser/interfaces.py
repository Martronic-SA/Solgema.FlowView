from zope.interface import Interface
        
class ISFWUtility(Interface):
    """
    utility methods for flowview
    """
    
    def should_include(filename):
        """
        This method can be called from an include expression for css/javascript
        to check if a file should be included for the flowview.
        """
        
    def enabled():
        """
        Lets you know if the flowview is enabled
        """
