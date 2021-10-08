# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 11:52:26 2018

@author: Simon Kern
"""

import os
import ospath
import unittest

class OsPathTest(unittest.TestCase):
    
    def test_join(self):
        linux = 'path/to/////folder/is//'
        windows = 'path\\to\\\\folder\\is'
        add = 'tesfile.txt'
        should_be = 'path/to/folder/is/tesfile.txt'
        self.assertEqual(ospath.join(linux, add), should_be)
        self.assertEqual(ospath.join(windows, add), should_be)
        
        lead_slash = '/path/to/folder/is'
        joined = ospath.join(lead_slash, lead_slash)
        self.assertEqual(joined, '/path/to/folder/is/path/to/folder/is')
        
    def test_splitext(self):
        path = 'path\\to/file//file.file.txt'
        ext  = ospath.splitext(path)
        self.assertEqual(ext, ('path/to/file/file.file', '.txt' ))
        
    def test_splitdrive(self):
        # this can only be tested on windwos
        path  = 'c:/path\\to/file//file.file.txt'
        drive  = ospath.splitdrive(path)
        
    def test_expanduser(self)  :
        path  = '~'
        user = ospath.expanduser(path)
        # this is user-specific, so hard to check if it's true
        self.assertTrue((user!='~') and (user!=''))
        
    def test_abspath(self)  :
        path    = './relative'
        absp = ospath.abspath(path)
        # this is folder-specific, so hard to check
        self.assertTrue(absp.endswith('relative') and (len(absp)>len(path)+1))
        
    def test_commonpath(self):
        path1    = '/path/is/here/relative'
        path2    = '/path/is/'   
        common = ospath.commonpath([path1,path2])
        self.assertEqual(common, '/path/is')

    def test_list_files(self):
        path = '.'
        files = ospath.list_files(path)
        self.assertEqual(len(files), 1)
        self.assertIn('/ospath_ut.py', files[0])
        
        files = ospath.list_files(path, relative=True)
        self.assertEqual(len(files), 1)
        self.assertEqual('ospath_ut.py', files[0])
        
        files = ospath.list_files(path, exts='png')
        self.assertEqual(len(files), 0)
        
        files = ospath.list_files(path, exts='png', subfolders=True)
        self.assertEqual(len(files), 6)

        files = ospath.list_files(path, exts='*image1*', subfolders=True)
        self.assertEqual(len(files), 0)

        files = ospath.list_files(path, patterns='*image1*', subfolders=True)
        self.assertEqual(len(files), 8)
        
        files = ospath.list_files(path, exts=['png', '.jpg', 'txt'], subfolders=True)
        self.assertEqual(len(files), 10)
        
        files = ospath.list_files(path, exts=['.png', '.jpg', 'txt'], subfolders=True)
        self.assertEqual(len(files), 8)  
        
        files = ospath.list_files(path, exts=['.png', '.jpg', 'txt'], patterns='*_ut*', subfolders=True)
        self.assertEqual(len(files), 9)        
        
        files = ospath.list_files(path, exts=['.png', '.jpg', 'txt'], patterns=['*_ut*'], subfolders=True)
        self.assertEqual(len(files), 9)        
        
        files = ospath.list_files(path, patterns=['**/*txt'], subfolders=False)
        self.assertEqual(len(files), 2)    
        
        files = ospath.list_files(path, subfolders=True)
        self.assertEqual(len(files),15)
        for file in files:
            self.assertTrue(ospath.isfile(file))
            self.assertTrue(ospath.exists(file))

        files = ospath.list_files(path, subfolders=True, relative=True, return_strings=False)
        self.assertEqual(len(files),15)
        for file in files:
            self.assertTrue(ospath.isfile(file))
            self.assertTrue(ospath.exists(file))
            self.assertFalse(isinstance(file, str))
            
    def test_list_folders(self):
        path = ospath.abspath('.')
        os.makedirs(path + '/subfolder/sub1', exist_ok=True)
        os.makedirs(path + '/subfolder/sub2', exist_ok=True)
        os.makedirs(path + '/subfolder/sub3', exist_ok=True)
        os.makedirs(path + '/subfolder/sub3/sub4', exist_ok=True)

        os.makedirs(path + '/subfolder/notincluded/sub5', exist_ok=True)
        os.makedirs(path + '/subfolder/notincluded/notincluded', exist_ok=True)

        folders = ospath.list_folders(path, subfolders = False, add_parent = False,
                                      pattern='sub*')
        self.assertIn('subfolder', folders[0])
        self.assertEqual(len(folders), 1)
        
        folders = ospath.list_folders(path, subfolders = True, add_parent = False,
                                      pattern='sub*')
        self.assertEqual(len(folders), 7)
        for f in folders:
            self.assertIn('sub', ospath.split(f)[-1])
                
        folders = ospath.list_folders(path, subfolders = True, add_parent = True,
                                      pattern='sub*')
        self.assertEqual(len(folders), 8)
        for f in folders[1:]:
            self.assertIn('sub', ospath.split(f)[-1])
                
        

if __name__ == '__main__':
    unittest.main()
    
    
    
    
    