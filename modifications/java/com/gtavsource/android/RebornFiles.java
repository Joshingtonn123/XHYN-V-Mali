package com.gtavsource.android;
import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.security.*;

public final class RebornFiles {
 static final int TEXT_LIMIT=65536;
 static byte[] bytes(InputStream in,int limit)throws IOException {
  ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[8192];int n;
  while((n=in.read(buf))!=-1){if(out.size()+n>limit)throw new IOException("File exceeds "+limit+" bytes");out.write(buf,0,n);}return out.toByteArray();
 }
 static String utf8(byte[] data)throws IOException {
  try {String s=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(data)).toString();
   if(s.startsWith("\ufeff"))s=s.substring(1);if(s.indexOf('\0')>=0)throw new IOException("Text contains a NUL character");return s.replace("\r\n","\n");
  }catch(CharacterCodingException e){throw new IOException("Use a UTF-8 text file",e);}
 }
 static String read(File f,int limit)throws IOException {try(InputStream in=new FileInputStream(f)){return utf8(bytes(in,limit));}}
 static void atomic(File target,String value)throws IOException {atomic(target,value.getBytes(StandardCharsets.UTF_8));}
 static void atomic(File target,byte[] value)throws IOException {
  File parent=target.getParentFile();if(!parent.isDirectory()&&!parent.mkdirs())throw new IOException("Cannot create "+parent);
  if(Files.isSymbolicLink(target.toPath()))throw new IOException("Refusing a symbolic link: "+target.getName());
  File temp=File.createTempFile(".reborn-",".tmp",parent);
  try{try(FileOutputStream out=new FileOutputStream(temp)){out.write(value);out.getFD().sync();}
   try{Files.move(temp.toPath(),target.toPath(),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
   catch(AtomicMoveNotSupportedException e){Files.move(temp.toPath(),target.toPath(),StandardCopyOption.REPLACE_EXISTING);}
  }finally{temp.delete();}
 }
 static String hex(byte[] value){StringBuilder s=new StringBuilder();for(byte b:value)s.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return s.toString();}
 static String sha(String s)throws Exception {return hex(MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8)));}
 static String sha(File file)throws Exception {MessageDigest d=MessageDigest.getInstance("SHA-256");byte[] buf=new byte[65536];try(InputStream in=new FileInputStream(file)){int n;while((n=in.read(buf))!=-1)d.update(buf,0,n);}return hex(d.digest());}
 static File directory(File p,String name)throws IOException {File f=new File(p,name);if(!f.isDirectory()&&!f.mkdirs())throw new IOException("Cannot create "+f);return f;}
}
